import os
import subprocess
import random
import threading
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, current_app, abort, jsonify
from werkzeug.utils import secure_filename
from models import db, Video, User, Reaction, Subscription, Comment, ViewHistory, Playlist, PlaylistVideo, WatchLater
from flask_login import current_user, login_required
from datetime import datetime

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

main_bp = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.app_template_filter('format_date')
def format_date(date):
    return date.strftime('%b %d, %Y')


@main_bp.route('/')
def home():
    # Base query for visible videos
    base_query = Video.query
    if current_user.is_authenticated:
        base_query = base_query.filter((Video.is_public == True) | (Video.user_id == current_user.id))
    else:
        base_query = base_query.filter_by(is_public=True)
    
    # 1. Latest (Sort by date)
    latest = base_query.order_by(Video.upload_date.desc()).limit(4).all()
    
    # 2. Trending (Sort by views)
    trending = base_query.order_by(Video.views.desc()).limit(4).all()
    
    # 3. For You & 4. From Channel (Personalized)
    for_you = []
    featured_channel = None
    channel_videos = []
    show_extra_sections = False
    
    if current_user.is_authenticated:
        try:
            from recommendations import get_recommendations, get_channel_recommendation
            # Check if user has any history
            has_history = ViewHistory.query.filter_by(user_id=current_user.id).count() > 0
            
            if has_history:
                for_you = get_recommendations(current_user.id, limit=4)
                featured_channel, channel_videos = get_channel_recommendation(current_user.id)
                show_extra_sections = True
            else:
                # New user: Fill For You with random/trending, hide others
                all_public = Video.query.filter_by(is_public=True).all()
                for_you = random.sample(all_public, min(len(all_public), 4)) if all_public else []
                show_extra_sections = False
        except Exception as e:
            print(f"Recommendation error: {e}")
            # Fallback on error
            all_public = Video.query.filter_by(is_public=True).all()
            for_you = random.sample(all_public, min(len(all_public), 4)) if all_public else []
    else:
        # Guest: Fill For You with random, hide others
        all_public = Video.query.filter_by(is_public=True).all()
        for_you = random.sample(all_public, min(len(all_public), 4)) if all_public else []
        show_extra_sections = False

    # If we are hiding extra sections, clear them
    if not show_extra_sections:
        latest = []
        trending = []
        featured_channel = None
        channel_videos = []

    return render_template('home.html', title='Home', 
                           for_you=for_you, 
                           latest=latest, 
                           trending=trending, 
                           featured_channel=featured_channel, 
                           channel_videos=channel_videos)


@main_bp.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    # Only allow watching private videos if owner
    if not video.is_public:
        if not (current_user.is_authenticated and current_user.id == video.user_id):
            abort(404)

    try:
        # increment views for non-owner viewers
        if not (current_user.is_authenticated and current_user.id == video.user_id):
            video.views = (video.views or 0) + 1
            # Record history if authenticated
            if current_user.is_authenticated:
                vh = ViewHistory(user_id=current_user.id, video_id=video.id)
                db.session.add(vh)
            db.session.commit()
    except Exception:
        db.session.rollback()
    
    # recommended: use ML engine for logged in users, else fallback
    recommended = []
    if current_user.is_authenticated:
        try:
            from recommendations import get_recommendations
            recommended = get_recommendations(current_user.id, limit=10, exclude_video_ids=[video_id])
        except Exception:
            pass
            
    # Fallback if empty (new user or guest)
    if not recommended:
        # Try same category first
        base_q = Video.query.filter(Video.id != video_id, Video.is_public == True)
        if video.category:
            recommended = base_q.filter_by(category=video.category).order_by(db.func.random()).limit(5).all()
        
        # If still not enough, fill with random
        if len(recommended) < 5:
            exclude = [v.id for v in recommended] + [video_id]
            others = Video.query.filter(~Video.id.in_(exclude), Video.is_public == True).order_by(db.func.random()).limit(5 - len(recommended)).all()
            recommended.extend(others)
    
    # compute reactions counts
    likes = Reaction.query.filter_by(video_id=video_id, type=1).count()
    dislikes = Reaction.query.filter_by(video_id=video_id, type=-1).count()
    
    # fetch comments
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.date_posted.desc()).all()
    
    is_liked = False
    is_disliked = False
    is_subscribed = False
    if current_user and current_user.is_authenticated:
        r = Reaction.query.filter_by(video_id=video_id, user_id=current_user.id).first()
        if r:
            is_liked = (r.type == 1)
            is_disliked = (r.type == -1)
        s = Subscription.query.filter_by(subscriber_id=current_user.id, channel_id=video.user_id).first()
        is_subscribed = bool(s)
    
    user_playlists = []
    is_watch_later = False
    is_saved = False
    saved_playlist_ids = []
    if current_user.is_authenticated:
        user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()
        is_watch_later = WatchLater.query.filter_by(user_id=current_user.id, video_id=video_id).first() is not None
        if user_playlists:
            p_ids = [p.id for p in user_playlists]
            existing = PlaylistVideo.query.filter(PlaylistVideo.playlist_id.in_(p_ids), PlaylistVideo.video_id == video_id).all()
            saved_playlist_ids = [e.playlist_id for e in existing]
            is_saved = len(saved_playlist_ids) > 0

    # detect auto-generated captions file (if any) matching the uploaded filename base
    auto_caption_url = ''
    try:
        if getattr(video, 'auto_captions', None):
            auto_caption_url = url_for('main.uploaded_file', filename=video.auto_captions)
        else:
            base = os.path.splitext(video.filename)[0]
            for fname in os.listdir(current_app.config['UPLOAD_FOLDER']):
                if fname.startswith(base) and fname.endswith('_auto.vtt'):
                    auto_caption_url = url_for('main.uploaded_file', filename=fname)
                    break
    except Exception:
        auto_caption_url = ''

    return render_template('watch.html', title=video.title, video=video, recommended=recommended,
                           likes=likes, dislikes=dislikes, is_liked=is_liked, is_disliked=is_disliked,
                           is_subscribed=is_subscribed, comments=comments, user_playlists=user_playlists, is_watch_later=is_watch_later, is_saved=is_saved,
                           saved_playlist_ids=saved_playlist_ids, auto_caption_url=auto_caption_url)


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('main.upload'))
        file = request.files['file']
        title = request.form.get('title') or 'Untitled'
        description = request.form.get('description') or ''
        category = request.form.get('category')
        tags = request.form.get('tags')

        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('main.upload'))

        visibility = request.form.get('visibility', 'public')
        is_public = True if visibility == 'public' else False

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            save_name = f"{timestamp}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], save_name)
            file.save(save_path)

            captions_file = request.files.get('captions')
            captions_path = None
            if captions_file and captions_file.filename != '':
                c_filename = secure_filename(captions_file.filename)
                c_save_name = f"{timestamp}_{c_filename}"
                c_save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], c_save_name)
                captions_file.save(c_save_path)
                captions_path = c_save_name

            # create video record first (thumbnail will be generated asynchronously)
            new_video = Video(
                title=title,
                description=description,
                filename=save_name,
                user_id=current_user.id,
                is_public=is_public,
                thumbnail=None,
                category=category,
                tags=tags,
                captions=captions_path
            )
            db.session.add(new_video)
            db.session.commit()

            # Start background thread to generate thumbnail without blocking upload
            def _generate_thumbnail(app, vid_id, saved_path, orig_filename, ts):
                try:
                    with app.app_context():
                        # get duration
                        probe_cmd = [
                            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', saved_path
                        ]
                        proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                        duration = None
                        if proc.returncode == 0:
                            try:
                                duration = float(proc.stdout.strip())
                            except Exception:
                                duration = None

                        if duration and duration > 2:
                            t = random.uniform(max(1.0, 0.1 * duration), max(1.5, 0.9 * duration))
                        else:
                            t = 1.0

                        thumbs_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')
                        os.makedirs(thumbs_dir, exist_ok=True)
                        thumb_name = f"{ts}_{os.path.splitext(orig_filename)[0]}.jpg"
                        thumb_path = os.path.join(thumbs_dir, thumb_name)

                        ff_cmd = [
                            'ffmpeg', '-ss', str(t), '-i', saved_path,
                            '-frames:v', '1', '-q:v', '2', thumb_path, '-y'
                        ]
                        subprocess.run(ff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)

                        # update video record with thumbnail path if file created
                        if os.path.exists(thumb_path):
                            rel = os.path.join('thumbnails', thumb_name)
                            v = Video.query.get(vid_id)
                            if v:
                                v.thumbnail = rel
                                db.session.commit()
                except Exception:
                    try:
                        db.session.rollback()
                    except Exception:
                        pass

            app_obj = current_app._get_current_object()
            thread = threading.Thread(target=_generate_thumbnail, args=(app_obj, new_video.id, save_path, filename, timestamp))
            thread.daemon = True
            thread.start()

            # Start background thread to auto-generate captions (does not overwrite user-provided captions)
            def _generate_captions(app, vid_id, saved_path, orig_filename, ts):
                try:
                    with app.app_context():
                        import shutil, subprocess, wave, json
                        import speech_recognition as sr
                        from vosk import Model, KaldiRecognizer
                        UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

                        base = os.path.splitext(orig_filename)[0]
                        auto_name = f"{ts}_{base}_auto.vtt"
                        auto_path = os.path.join(UPLOAD_FOLDER, auto_name)

                        # Extract audio to WAV
                        wav_path = os.path.join(UPLOAD_FOLDER, f"{ts}_{base}_audio.wav")
                        try:
                            subprocess.run(['ffmpeg', '-i', saved_path, '-ac', '1', '-ar', '16000', wav_path, '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=120)
                        except Exception:
                            if os.path.exists(wav_path): os.remove(wav_path)
                            return

                        duration = None
                        try:
                            proc = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', saved_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                            if proc.returncode == 0:
                                duration = float(proc.stdout.strip())
                        except Exception:
                            duration = None

                        transcript = ''
                        # try Vosk offline if available
                        try:
                            model_path = app.config.get('VOSK_MODEL_PATH')
                            if model_path and os.path.exists(model_path):
                                wf = wave.open(wav_path, 'rb')
                                model = Model(model_path)
                                rec = KaldiRecognizer(model, wf.getframerate())
                                rec.SetWords(False)
                                while True:
                                    buf = wf.readframes(4000)
                                    if len(buf) == 0: break
                                    rec.AcceptWaveform(buf)
                                final = json.loads(rec.FinalResult())
                                transcript = final.get('text', '')
                                wf.close()
                        except Exception:
                            transcript = ''

                        # fallback to Google (requires internet)
                        if not transcript:
                            try:
                                r = sr.Recognizer()
                                with sr.AudioFile(wav_path) as source:
                                    audio_data = r.record(source)
                                    transcript = r.recognize_google(audio_data)
                            except Exception:
                                transcript = ''

                        # Build simple WebVTT by chunking words across duration
                        if transcript:
                            words = transcript.split()
                            if duration and duration > 0:
                                cue_len = 4.0
                                cues = []
                                i = 0
                                wps = len(words) / duration if duration>0 else 2
                                while i < len(words):
                                    start_sec = (i / wps) if wps>0 else 0
                                    j = i + int(cue_len * wps)
                                    if j <= i: j = min(i+10, len(words))
                                    end_sec = (j / wps) if wps>0 else (start_sec + cue_len)
                                    text = ' '.join(words[i:j])
                                    cues.append((start_sec, end_sec, text))
                                    i = j
                            else:
                                cues = [(0.0, max(4.0, len(transcript.split())/2.0), transcript)]

                            try:
                                with open(auto_path, 'w', encoding='utf-8') as f:
                                    f.write('WEBVTT\n\n')
                                    for s,e,t in cues:
                                        def fmt(x):
                                            h = int(x//3600); m = int((x%3600)//60); sss = int(x%60); ms = int((x - int(x))*1000)
                                            return f"{h:02d}:{m:02d}:{sss:02d}.{ms:03d}"
                                        f.write(f"{fmt(s)} --> {fmt(e)}\n{t}\n\n")
                                # update DB record with auto caption filename
                                try:
                                    v = Video.query.get(vid_id)
                                    if v:
                                        v.auto_captions = auto_name
                                        db.session.commit()
                                except Exception:
                                    try: db.session.rollback()
                                    except Exception: pass
                            except Exception:
                                pass

                        if os.path.exists(wav_path):
                            try: os.remove(wav_path)
                            except Exception: pass
                except Exception:
                    try:
                        pass
                    except Exception:
                        pass

            cap_thread = threading.Thread(target=_generate_captions, args=(app_obj, new_video.id, save_path, filename, timestamp))
            cap_thread.daemon = True
            cap_thread.start()

            return redirect(url_for('main.home'))
        else:
            flash('File type not allowed')
            return redirect(url_for('main.upload'))

    return render_template('upload.html', title='Upload')


@main_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash('Not authorized')
        return redirect(url_for('main.watch', video_id=video_id))
    # delete file from disk if exists
    try:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], video.filename)
        if os.path.exists(path):
            os.remove(path)
        # delete thumbnail if present
        if video.thumbnail:
            tpath = os.path.join(current_app.config['UPLOAD_FOLDER'], video.thumbnail)
            if os.path.exists(tpath):
                os.remove(tpath)
    except Exception:
        pass
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted')
    return redirect(url_for('main.home'))


@main_bp.route('/video/<int:video_id>/visibility', methods=['POST'])
@login_required
def toggle_visibility(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash('Not authorized')
        return redirect(url_for('main.watch', video_id=video_id))
    new_vis = request.form.get('visibility')
    video.is_public = True if new_vis == 'public' else False
    db.session.commit()
    flash('Visibility updated')
    return redirect(url_for('main.watch', video_id=video_id))


@main_bp.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # show public videos or owner-only
    if current_user.is_authenticated and current_user.id == user.id:
        videos = Video.query.filter_by(user_id=user.id).order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.filter_by(user_id=user.id, is_public=True).order_by(Video.upload_date.desc()).all()

    # subscription info
    from models import Subscription
    subs_count = Subscription.query.filter_by(channel_id=user.id).count()
    is_subscribed = False
    if current_user.is_authenticated:
        is_subscribed = Subscription.query.filter_by(channel_id=user.id, subscriber_id=current_user.id).first() is not None

    # Playlists and Watch Later (only for owner)
    playlists = []
    watch_later_videos = []
    if current_user.is_authenticated and current_user.id == user.id:
        playlists = Playlist.query.filter_by(user_id=user.id).order_by(Playlist.created_at.desc()).all()
        wl_items = WatchLater.query.filter_by(user_id=user.id).order_by(WatchLater.added_at.desc()).all()
        watch_later_videos = [item.video for item in wl_items]

    return render_template('user.html', title=user.display_name or user.username, channel=user, videos=videos, subs_count=subs_count, is_subscribed=is_subscribed, playlists=playlists, watch_later_videos=watch_later_videos)


def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax')

@main_bp.route('/subscribe/<int:channel_id>', methods=['POST'])
def subscribe(channel_id):
    if not current_user.is_authenticated:
        if is_ajax(request):
            return jsonify({'error': 'login_required', 'redirect': url_for('auth.login')}), 401
        flash('Please sign in to subscribe')
        return redirect(url_for('auth.login'))
    
    if channel_id == current_user.id:
        flash('Cannot subscribe to yourself')
        return redirect(url_for('main.home'))
    
    channel = User.query.get_or_404(channel_id)
    existing = Subscription.query.filter_by(channel_id=channel_id, subscriber_id=current_user.id).first()
    if existing:
        try:
            db.session.delete(existing)
            db.session.commit()
            flash('Unsubscribed')
            if is_ajax(request):
                subs_count = Subscription.query.filter_by(channel_id=channel_id).count()
                return jsonify({'subscribed': False, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to unsubscribe')
    else:
        try:
            sub = Subscription(channel_id=channel_id, subscriber_id=current_user.id)
            db.session.add(sub)
            db.session.commit()
            flash('Subscribed')
            if is_ajax(request):
                subs_count = Subscription.query.filter_by(channel_id=channel_id).count()
                return jsonify({'subscribed': True, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to subscribe')
    return redirect(url_for('main.user_profile', username=channel.username))


@main_bp.route('/video/<int:video_id>/react', methods=['POST'])
def react_video(video_id):
    # Check authentication first for AJAX requests
    if not current_user.is_authenticated:
        if is_ajax(request):
            return jsonify({'error': 'Not authenticated', 'redirect': url_for('auth.login')}), 401
        flash('Please log in to react to videos')
        return redirect(url_for('auth.login'))
    
    video = Video.query.get_or_404(video_id)
    action = request.form.get('action')
    if not action and request.is_json:
        data = request.get_json()
        if data:
            action = data.get('action')
    if action not in ('like', 'dislike'):
        if is_ajax(request):
            return jsonify({'error': 'Invalid action'}), 400
        flash('Invalid reaction')
        return redirect(url_for('main.watch', video_id=video_id))
    
    t = 1 if action == 'like' else -1
    existing = Reaction.query.filter_by(video_id=video.id, user_id=current_user.id).first()
    try:
        if existing:
            if existing.type == t:
                # undo
                db.session.delete(existing)
                db.session.commit()
                flash('Reaction removed')
            else:
                existing.type = t
                db.session.commit()
                flash('Reaction updated')
        else:
            r = Reaction(video_id=video.id, user_id=current_user.id, type=t)
            db.session.add(r)
            db.session.commit()
            flash('Reaction recorded')
    except Exception:
        db.session.rollback()
        flash('Failed to record reaction')
    
    # For AJAX requests return JSON with updated counts and state
    if is_ajax(request):
        likes = Reaction.query.filter_by(video_id=video.id, type=1).count()
        dislikes = Reaction.query.filter_by(video_id=video.id, type=-1).count()
        r = Reaction.query.filter_by(video_id=video.id, user_id=current_user.id).first()
        return jsonify({'likes': likes, 'dislikes': dislikes, 'is_liked': bool(r and r.type == 1), 'is_disliked': bool(r and r.type == -1)})
    
    return redirect(url_for('main.watch', video_id=video_id))

@main_bp.route('/video/<int:video_id>/comment', methods=['POST'])
def add_comment(video_id):
    if not current_user.is_authenticated:
        if is_ajax(request):
            return jsonify({'error': 'Not authenticated', 'redirect': url_for('auth.login')}), 401
        flash('Please log in to comment')
        return redirect(url_for('auth.login'))
    
    video = Video.query.get_or_404(video_id)
    content = request.form.get('content')
    
    if request.is_json:
        data = request.get_json()
        if data:
            content = data.get('content')
            
    if not content or not content.strip():
        if is_ajax(request):
            return jsonify({'error': 'Comment cannot be empty'}), 400
        flash('Comment cannot be empty')
        return redirect(url_for('main.watch', video_id=video_id))
        
    comment = Comment(content=content.strip(), user_id=current_user.id, video_id=video.id)
    db.session.add(comment)
    db.session.commit()
    
    if is_ajax(request):
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': current_user.display_name or current_user.username,
                'user_url': url_for('main.user_profile', username=current_user.username),
                'profile_pic': url_for('main.uploaded_file', filename=current_user.profile_pic) if current_user.profile_pic else None,
                'initial': current_user.username[0].upper(),
                'date': format_date(comment.date_posted)
            }
        })
        
    flash('Comment added')
    return redirect(url_for('main.watch', video_id=video_id))

@main_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Allow deletion if user is the commenter OR the video owner
    if comment.user_id != current_user.id and comment.video.user_id != current_user.id:
        if is_ajax(request):
            return jsonify({'error': 'Not authorized'}), 403
        flash('Not authorized')
        return redirect(url_for('main.watch', video_id=comment.video_id))
        
    video_id = comment.video_id
    db.session.delete(comment)
    db.session.commit()
    
    if is_ajax(request):
        return jsonify({'success': True})
        
    flash('Comment deleted')
    return redirect(url_for('main.watch', video_id=video_id))


@main_bp.route('/playlists')
@login_required
def playlists():
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.created_at.desc()).all()
    return render_template('playlists.html', title='My Playlists', playlists=user_playlists)


@main_bp.route('/playlist/create', methods=['POST'])
@login_required
def create_playlist():
    name = request.form.get('name')
    if name:
        p = Playlist(name=name, user_id=current_user.id)
        db.session.add(p)
        db.session.commit()
        flash('Playlist created')
    return redirect(url_for('main.playlists'))


@main_bp.route('/playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if not playlist.is_public and (not current_user.is_authenticated or current_user.id != playlist.user_id):
        abort(403)
    
    videos = [pv.video for pv in playlist.videos]
    return render_template('playlist.html', title=playlist.name, playlist=playlist, videos=videos)


@main_bp.route('/playlist/<int:playlist_id>/add/<int:video_id>', methods=['POST'])
@login_required
def add_to_playlist(playlist_id, video_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        abort(403)
    
    exists = PlaylistVideo.query.filter_by(playlist_id=playlist_id, video_id=video_id).first()
    if not exists:
        pv = PlaylistVideo(playlist_id=playlist_id, video_id=video_id)
        db.session.add(pv)
        db.session.commit()
        if is_ajax(request):
            return jsonify({'success': True, 'is_saved_in_any': True})
        flash('Added to playlist')
    else:
        if is_ajax(request):
            return jsonify({'success': False, 'message': 'Already in playlist', 'is_saved_in_any': True})
            
    return redirect(url_for('main.watch', video_id=video_id))


@main_bp.route('/playlist/<int:playlist_id>/remove/<int:video_id>', methods=['POST'])
@login_required
def remove_from_playlist(playlist_id, video_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        abort(403)
        
    pv = PlaylistVideo.query.filter_by(playlist_id=playlist_id, video_id=video_id).first()
    if pv:
        db.session.delete(pv)
        db.session.commit()
        
        # Check if saved in any other playlist
        user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()
        is_saved_in_any = False
        if user_playlists:
            p_ids = [p.id for p in user_playlists]
            is_saved_in_any = PlaylistVideo.query.filter(PlaylistVideo.playlist_id.in_(p_ids), PlaylistVideo.video_id == video_id).first() is not None
            
        if is_ajax(request):
            return jsonify({'success': True, 'is_saved_in_any': is_saved_in_any})
        flash('Removed from playlist')
    
    return redirect(url_for('main.view_playlist', playlist_id=playlist_id))


@main_bp.route('/watch-later')
@login_required
def watch_later():
    wl_items = WatchLater.query.filter_by(user_id=current_user.id).order_by(WatchLater.added_at.desc()).all()
    videos = [item.video for item in wl_items]
    return render_template('watch_later.html', title='Watch Later', videos=videos)


@main_bp.route('/watch-later/add/<int:video_id>', methods=['POST'])
@login_required
def add_to_watch_later(video_id):
    exists = WatchLater.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    if not exists:
        wl = WatchLater(user_id=current_user.id, video_id=video_id)
        db.session.add(wl)
        db.session.commit()
        if is_ajax(request):
            return jsonify({'success': True, 'in_watch_later': True})
        flash('Added to Watch Later')
    else:
        if is_ajax(request):
            return jsonify({'success': False, 'message': 'Already in Watch Later', 'in_watch_later': True})
            
    return redirect(url_for('main.watch', video_id=video_id))


@main_bp.route('/watch-later/remove/<int:video_id>', methods=['POST'])
@login_required
def remove_from_watch_later(video_id):
    wl = WatchLater.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    if wl:
        db.session.delete(wl)
        db.session.commit()
        if is_ajax(request):
            return jsonify({'success': True, 'in_watch_later': False})
        flash('Removed from Watch Later')
    else:
        if is_ajax(request):
            return jsonify({'success': False, 'in_watch_later': False})

    return redirect(url_for('main.watch_later'))


@main_bp.route('/search')
def search():
    import voice
    query = request.args.get('q', '')
    if query:
        # Process natural language/voice commands
        clean_query = voice.process_command(query)
        videos = Video.query.filter(Video.title.contains(clean_query) | Video.description.contains(clean_query)).filter_by(is_public=True).all()
    else:
        videos = []
    return render_template('search.html', title='Search', videos=videos, query=query)


@main_bp.route('/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip()
    suggestions = []
    
    if query:
        # Search for videos matching the query
        # Use ilike for case-insensitive search if supported, or just contains
        videos = Video.query.filter(Video.title.contains(query)).filter_by(is_public=True).limit(5).all()
        suggestions = [{'text': v.title, 'type': 'video'} for v in videos]
    else:
        # Return trending (most viewed videos) as a proxy for trending searches
        trending = Video.query.filter_by(is_public=True).order_by(Video.views.desc()).limit(5).all()
        suggestions = [{'text': v.title, 'type': 'trending'} for v in trending]
        
    return jsonify(suggestions)


@main_bp.route('/voice_search', methods=['POST'])
def voice_search_api():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    import speech_recognition as sr
    import os
    import static_ffmpeg
    import uuid
    import shutil
    import subprocess
    import json
    from vosk import Model, KaldiRecognizer
    import wave
    
    try:
        static_ffmpeg.add_paths()
    except Exception:
        pass
    
    # Save temporary file
    unique_id = str(uuid.uuid4())
    temp_webm = os.path.join(current_app.config['UPLOAD_FOLDER'], f'temp_voice_{unique_id}.webm')
    temp_wav = os.path.join(current_app.config['UPLOAD_FOLDER'], f'temp_voice_{unique_id}.wav')
    
    try:
        if not shutil.which('ffmpeg'):
            # Fallback: try to find it in static_ffmpeg location manually if add_paths failed
            import sys
            bin_path = os.path.join(sys.prefix, 'bin')
            if os.path.exists(os.path.join(bin_path, 'ffmpeg')):
                os.environ["PATH"] += os.pathsep + bin_path
            
            if not shutil.which('ffmpeg'):
                return jsonify({'error': 'Server Error: ffmpeg binary not found'}), 500

        audio_file.save(temp_webm)
        
        # Convert WebM to WAV using ffmpeg (SpeechRecognition needs WAV/AIFF/FLAC)
        # -y to overwrite, -ac 1 for mono (optional but good for SR)
        cmd = ['ffmpeg', '-i', temp_webm, '-ac', '1', '-ar', '16000', temp_wav, '-y']
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Try Offline (Vosk) first if model exists
        model_path = current_app.config.get('VOSK_MODEL_PATH')
        if model_path and os.path.exists(model_path):
            try:
                model = Model(model_path)
                wf = wave.open(temp_wav, "rb")
                rec = KaldiRecognizer(model, wf.getframerate())
                rec.SetWords(True)
                
                result_text = ""
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        pass
                    else:
                        pass
                
                final_res = json.loads(rec.FinalResult())
                text = final_res.get('text', '')
                wf.close()
                
                if text:
                    return jsonify({'text': text})
            except Exception as e:
                print(f"Vosk error: {e}")
                # Fallback to Google if Vosk fails
        
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = r.record(source)
            # Try Google first (high accuracy, requires internet on server)
            try:
                text = r.recognize_google(audio_data)
                return jsonify({'text': text})
            except sr.UnknownValueError:
                return jsonify({'error': 'Could not understand audio'}), 400
            except sr.RequestError as e:
                print(f"Speech service error: {e}")
                return jsonify({'error': 'Speech service unavailable'}), 503
                
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg error: {err_msg}")
        return jsonify({'error': 'Audio conversion failed'}), 500
    except Exception as e:
        print(f"Voice search error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Voice processing failed'}), 500
    finally:
        # Cleanup
        if os.path.exists(temp_webm):
            os.remove(temp_webm)
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
