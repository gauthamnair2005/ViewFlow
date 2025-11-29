import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from jinja2 import DictLoader
import cv2
import random

__version__ = '0.3.1'

# ==========================================
# CONFIGURATION
# ==========================================
# file system and app configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-gautham-deepak'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'viewflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
# Use filesystem templates from the `templates/` directory so edits there are reflected.
# If you prefer the in-memory templates for tests, uncomment the DictLoader block below.
# app.jinja_loader = DictLoader({
#     'base.html': BASE_HTML,
#     'home.html': HOME_HTML,
#     'watch.html': WATCH_HTML,
#     'login.html': LOGIN_HTML,
#     'register.html': REGISTER_HTML,
#     'upload.html': UPLOAD_HTML
# })

# ==========================================
# DATABASE MODELS
# ==========================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(150), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(200), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(300), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    videos = db.relationship('Video', backref='uploader', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(200), nullable=True)
    views = db.Column(db.Integer, default=0)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    # type: 1 = like, -1 = dislike
    type = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# UTILITIES
# ==========================================

def allowed_file(filename, file_type='video'):
    """Check if file extension is allowed.
    file_type can be 'video' or 'image'
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    return False

def generate_thumbnail(video_path, output_path):
    """Generate a thumbnail from a random frame in the video"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        # Get total frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return None
        
        # Pick a random frame (avoid first and last 10%)
        start_frame = int(total_frames * 0.1)
        end_frame = int(total_frames * 0.9)
        random_frame = random.randint(start_frame, end_frame) if end_frame > start_frame else total_frames // 2
        
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Resize to standard thumbnail size (320x180)
            thumbnail = cv2.resize(frame, (320, 180))
            cv2.imwrite(output_path, thumbnail)
            return True
        return None
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

def format_date(date):
    if not date:
        return 'Unknown'
    return date.strftime('%b %d, %Y')

app.jinja_env.filters['format_date'] = format_date


# --------------------------
# Database / Uploads Init
# --------------------------
def init_db():
    """Create uploads directory, database tables, and run best-effort migrations.
    This is executed on app import so the test server can start even if the DB
    file does not yet exist.
    """
    # ensure uploads dir exists
    try:
        os.makedirs(app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER), exist_ok=True)
    except Exception:
        pass

    with app.app_context():
        try:
            db.create_all()
            print("Database initialized.")
        except Exception:
            # continue even if create_all fails
            pass

        # best-effort sqlite ALTER TABLE migrations for test environment
        try:
            inspector = inspect(db.engine)
            # video table columns
            try:
                video_cols = [c['name'] for c in inspector.get_columns('video')]
            except Exception:
                video_cols = []
            with db.engine.connect() as conn:
                if 'is_public' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN is_public BOOLEAN DEFAULT 1"))
                        conn.commit()
                    except Exception:
                        pass
                if 'thumbnail' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN thumbnail VARCHAR(200)"))
                        conn.commit()
                    except Exception:
                        pass

            # user table columns
            try:
                user_cols = [c['name'] for c in inspector.get_columns('user')]
            except Exception:
                user_cols = []
            with db.engine.connect() as conn:
                if 'display_name' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN display_name VARCHAR(150)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'location' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN location VARCHAR(200)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'age' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN age INTEGER"))
                        conn.commit()
                    except Exception:
                        pass
                if 'date_joined' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN date_joined DATETIME"))
                        conn.commit()
                    except Exception:
                        pass
                if 'gender' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN gender VARCHAR(50)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'profile_pic' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN profile_pic VARCHAR(300)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'bio' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN bio TEXT"))
                        conn.commit()
                    except Exception:
                        pass
        except Exception:
            # if inspector or engine access fails, just continue
            pass


# Initialize DB and uploads at import time so the app is ready on start
init_db()

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def home():
    # Show public videos to everyone; owners see their own videos too
    if current_user and current_user.is_authenticated:
        videos = Video.query.filter(
            (Video.is_public == True) | (Video.user_id == current_user.id)
        ).order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.filter_by(is_public=True).order_by(Video.upload_date.desc()).all()
    return render_template('home.html', title="Home", videos=videos)


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('home'))
    
    # Search in video title, description, and uploader name
    search_pattern = f"%{query}%"
    videos = Video.query.join(Video.uploader).filter(
        (Video.is_public == True) &
        (
            (Video.title.ilike(search_pattern)) |
            (Video.description.ilike(search_pattern)) |
            (User.username.ilike(search_pattern)) |
            (User.display_name.ilike(search_pattern))
        )
    ).order_by(Video.upload_date.desc()).all()
    
    return render_template('search.html', title=f"Search: {query}", query=query, videos=videos)

@app.route('/test-async')
@login_required
def test_async():
    return render_template('test_async.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Login failed. Check your email and password.')
    return render_template('login.html', title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        display_name = request.form.get('display_name') or username
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        location = request.form.get('location')
        bio = request.form.get('bio')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('register'))
        
        # Handle profile picture upload
        profile_pic_path = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename and allowed_file(file.filename, 'image'):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                save_name = f"profile_{timestamp}_{filename}"
                
                save_path = os.path.join(UPLOAD_FOLDER, save_name)
                file.save(save_path)
                profile_pic_path = save_name
                print(f"[REGISTER] Saved profile picture: {save_name}")
            else:
                if file.filename:
                    print(f"[REGISTER] Profile picture rejected: {file.filename} (invalid format)")
            
        new_user = User(
            username=username,
            display_name=display_name,
            email=email, 
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            age=int(age) if age else None,
            gender=gender if gender else None,
            location=location if location else None,
            bio=bio if bio else None,
            profile_pic=profile_pic_path,
            date_joined=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Account created successfully!')
        return redirect(url_for('home'))
    return render_template('register.html', title="Register")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        title = request.form.get('title')
        description = request.form.get('description')
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename, 'video'):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            save_name = f"{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
            file.save(video_path)
            
            # Generate thumbnail
            thumbnail_name = f"{timestamp}_thumb.jpg"
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_name)
            generate_thumbnail(video_path, thumbnail_path)
            
            new_video = Video(
                title=title,
                description=description,
                filename=save_name,
                thumbnail=thumbnail_name if os.path.exists(thumbnail_path) else None,
                user_id=current_user.id
            )
            db.session.add(new_video)
            db.session.commit()
            return redirect(url_for('home'))
            
    return render_template('upload.html', title="Upload")

@app.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    # Only allow watching private videos if owner
    if not getattr(video, 'is_public', True):
        if not (current_user.is_authenticated and current_user.id == video.user_id):
            abort(404)

    try:
        # increment views for non-owner viewers
        is_owner = current_user.is_authenticated and current_user.id == video.user_id
        print(f"[VIEW DEBUG] Video: {video.title}, User: {current_user.username if current_user.is_authenticated else 'Anonymous'}, Owner: {is_owner}, Current Views: {video.views}")
        
        if not is_owner:
            old_views = video.views or 0
            video.views = old_views + 1
            db.session.commit()
            print(f"[VIEW DEBUG] Views incremented: {old_views} -> {video.views}")
        else:
            print(f"[VIEW DEBUG] Owner viewing - no increment")
    except Exception as e:
        print(f"[VIEW DEBUG] Error: {e}")
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Minimal stubs for endpoints referenced by templates originally written for a blueprint.
# These are lightweight and redirect back to home or the referrer so `url_for` works.
@app.route('/user/<string:username>')
def user_profile(username):
    # Render a simple channel page showing the user's public videos.
    channel = User.query.filter_by(username=username).first()
    if not channel:
        abort(404)

    # Ensure display_name attribute exists for templates (test DB may not have it)
    try:
        display_name_val = channel.display_name
    except Exception:
        display_name_val = None
    if not display_name_val:
        # attach a fallback attribute on the instance so templates can use it
        channel.display_name = channel.username
        display_name_val = channel.username

    # Show public videos; if current_user is the channel owner, show all their videos
    if current_user and current_user.is_authenticated and current_user.id == channel.id:
        videos = Video.query.filter_by(user_id=channel.id).order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.filter_by(user_id=channel.id, is_public=True).order_by(Video.upload_date.desc()).all()

    # compute subscribers count and whether current_user subscribes
    subs_count = Subscription.query.filter_by(channel_id=channel.id).count()
    is_subscribed = False
    if current_user and current_user.is_authenticated:
        is_subscribed = bool(Subscription.query.filter_by(channel_id=channel.id, subscriber_id=current_user.id).first())

    return render_template('user.html', title=display_name_val, channel=channel, videos=videos, subs_count=subs_count, is_subscribed=is_subscribed)


@app.route('/subscribe/<int:channel_id>', methods=['POST'])
def subscribe(channel_id):
    if not current_user.is_authenticated:
        # If AJAX request, return JSON for client to redirect to login
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'login_required', 'redirect': url_for('login')}), 401
        flash('Please sign in to subscribe')
        return redirect(request.referrer or url_for('login'))

    channel = User.query.get_or_404(channel_id)
    # toggle subscription
    existing = Subscription.query.filter_by(channel_id=channel.id, subscriber_id=current_user.id).first()
    if existing:
        try:
            db.session.delete(existing)
            db.session.commit()
            flash('Unsubscribed')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                subs_count = Subscription.query.filter_by(channel_id=channel.id).count()
                return jsonify({'subscribed': False, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to unsubscribe')
    else:
        try:
            sub = Subscription(channel_id=channel.id, subscriber_id=current_user.id)
            db.session.add(sub)
            db.session.commit()
            flash('Subscribed')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                subs_count = Subscription.query.filter_by(channel_id=channel.id).count()
                return jsonify({'subscribed': True, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to subscribe')
    # Default redirect for non-AJAX
    return redirect(request.referrer or url_for('user_profile', username=channel.username))


@app.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    # Only owner can delete
    if not (current_user.is_authenticated and current_user.id == video.user_id):
        flash('Not authorized to delete this video')
        return redirect(request.referrer or url_for('home'))

    # remove file from disk
    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        if os.path.exists(video_path):
            os.remove(video_path)
        # remove thumbnail if exists
        if getattr(video, 'thumbnail', None):
            thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], video.thumbnail)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
    except Exception:
        # continue even if file deletion fails
        pass

    # delete DB record
    try:
        db.session.delete(video)
        db.session.commit()
        flash('Video deleted')
    except Exception:
        db.session.rollback()
        flash('Failed to delete video')

    return redirect(url_for('home'))


@app.route('/video/<int:video_id>/visibility', methods=['POST'])
@login_required
def toggle_visibility(video_id):
    video = Video.query.get_or_404(video_id)
    # Only owner can change visibility
    if not (current_user.is_authenticated and current_user.id == video.user_id):
        flash('Not authorized')
        return redirect(request.referrer or url_for('home'))

    new_vis = request.form.get('visibility')
    video.is_public = True if new_vis == 'public' else False
    try:
        db.session.commit()
        flash('Visibility updated')
    except Exception:
        db.session.rollback()
        flash('Failed to update visibility')
    return redirect(url_for('watch', video_id=video_id))


@app.route('/video/<int:video_id>/react', methods=['POST'])
def react_video(video_id):
    # Check authentication first for AJAX requests
    if not current_user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Not authenticated', 'redirect': url_for('login')}), 401
        flash('Please log in to react to videos')
        return redirect(url_for('login'))
    
    video = Video.query.get_or_404(video_id)
    action = request.form.get('action')
    if action not in ('like', 'dislike'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid action'}), 400
        flash('Invalid reaction')
        return redirect(request.referrer or url_for('watch', video_id=video_id))

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

    return redirect(request.referrer or url_for('watch', video_id=video_id))

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Ensure new columns exist in sqlite table (simple migration for test environment)
        try:
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('video')]
            with db.engine.connect() as conn:
                if 'is_public' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN is_public BOOLEAN DEFAULT 1"))
                    except Exception:
                        pass
                if 'thumbnail' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN thumbnail VARCHAR(200)"))
                    except Exception:
                        pass
                # ensure user table has new profile columns
                try:
                    user_cols = [c['name'] for c in inspector.get_columns('user')]
                    if 'display_name' not in user_cols:
                        try:
                            conn.execute(text("ALTER TABLE user ADD COLUMN display_name VARCHAR(150)"))
                        except Exception:
                            pass
                    if 'location' not in user_cols:
                        try:
                            conn.execute(text("ALTER TABLE user ADD COLUMN location VARCHAR(150)"))
                        except Exception:
                            pass
                    if 'age' not in user_cols:
                        try:
                            conn.execute(text("ALTER TABLE user ADD COLUMN age INTEGER"))
                        except Exception:
                            pass
                    if 'date_joined' not in user_cols:
                        try:
                            conn.execute(text("ALTER TABLE user ADD COLUMN date_joined DATETIME"))
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            # If inspector or alter fails, continue; this is best-effort for the test DB
            pass
        print("Database initialized.")
        print("ViewFlow is running. Developed by Gautham Nair and Deepak Patel.")
        
    # Allow overriding port with PORT env var for local testing
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)