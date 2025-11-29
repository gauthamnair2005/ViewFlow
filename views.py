import os
import subprocess
import random
import threading
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, current_app, abort, jsonify
from werkzeug.utils import secure_filename
from models import db, Video, User, Reaction, Subscription
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
    # Show public videos to everyone; owners see their own videos too
    if current_user and current_user.is_authenticated:
        videos = Video.query.filter(
            (Video.is_public == True) | (Video.user_id == current_user.id)
        ).order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.filter_by(is_public=True).order_by(Video.upload_date.desc()).all()
    return render_template('home.html', title='Home', videos=videos)


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
            db.session.commit()
    except Exception:
        db.session.rollback()
    
    # recommended: only show public videos or owner's own videos
    if current_user and current_user.is_authenticated:
        recommended = Video.query.filter(
            (Video.id != video_id) & ((Video.is_public == True) | (Video.user_id == current_user.id))
        ).order_by(db.func.random()).limit(5).all()
    else:
        recommended = Video.query.filter(Video.id != video_id, Video.is_public == True).order_by(db.func.random()).limit(5).all()
    
    # compute reactions counts
    likes = Reaction.query.filter_by(video_id=video_id, type=1).count()
    dislikes = Reaction.query.filter_by(video_id=video_id, type=-1).count()
    
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
    
    return render_template('watch.html', title=video.title, video=video, recommended=recommended,
                           likes=likes, dislikes=dislikes, is_liked=is_liked, is_disliked=is_disliked,
                           is_subscribed=is_subscribed)


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        title = request.form.get('title') or 'Untitled'
        description = request.form.get('description') or ''

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        visibility = request.form.get('visibility', 'public')
        is_public = True if visibility == 'public' else False

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            save_name = f"{timestamp}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], save_name)
            file.save(save_path)

            # create video record first (thumbnail will be generated asynchronously)
            new_video = Video(
                title=title,
                description=description,
                filename=save_name,
                user_id=current_user.id,
                is_public=is_public,
                thumbnail=None
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

            return redirect(url_for('main.home'))
        else:
            flash('File type not allowed')
            return redirect(request.url)

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

    return render_template('user.html', title=user.display_name or user.username, channel=user, videos=videos, subs_count=subs_count, is_subscribed=is_subscribed)


@main_bp.route('/subscribe/<int:channel_id>', methods=['POST'])
def subscribe(channel_id):
    if not current_user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'login_required', 'redirect': url_for('auth.login')}), 401
        flash('Please sign in to subscribe')
        return redirect(request.referrer or url_for('auth.login'))
    
    if channel_id == current_user.id:
        flash('Cannot subscribe to yourself')
        return redirect(request.referrer or url_for('main.home'))
    
    channel = User.query.get_or_404(channel_id)
    existing = Subscription.query.filter_by(channel_id=channel_id, subscriber_id=current_user.id).first()
    if existing:
        try:
            db.session.delete(existing)
            db.session.commit()
            flash('Unsubscribed')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                subs_count = Subscription.query.filter_by(channel_id=channel_id).count()
                return jsonify({'subscribed': True, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to subscribe')
    return redirect(request.referrer or url_for('main.user_profile', username=channel.username))


@main_bp.route('/video/<int:video_id>/react', methods=['POST'])
def react_video(video_id):
    # Check authentication first for AJAX requests
    if not current_user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Not authenticated', 'redirect': url_for('auth.login')}), 401
        flash('Please log in to react to videos')
        return redirect(url_for('auth.login'))
    
    video = Video.query.get_or_404(video_id)
    action = request.form.get('action')
    if action not in ('like', 'dislike'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid action'}), 400
        flash('Invalid reaction')
        return redirect(request.referrer or url_for('main.watch', video_id=video_id))
    
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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        likes = Reaction.query.filter_by(video_id=video.id, type=1).count()
        dislikes = Reaction.query.filter_by(video_id=video.id, type=-1).count()
        r = Reaction.query.filter_by(video_id=video.id, user_id=current_user.id).first()
        return jsonify({'likes': likes, 'dislikes': dislikes, 'is_liked': bool(r and r.type == 1), 'is_disliked': bool(r and r.type == -1)})
    
    return redirect(request.referrer or url_for('main.watch', video_id=video_id))
