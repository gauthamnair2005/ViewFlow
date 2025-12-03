import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text, func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from jinja2 import DictLoader
import cv2
import random
from collections import Counter, defaultdict
import math
import voice
import speech_recognition as sr
import static_ffmpeg
import uuid
import shutil
import subprocess
import json
import threading
from vosk import Model, KaldiRecognizer
import wave
import markdown
import bleach

__version__ = '0.8.3'

# ==========================================
# CONFIGURATION
# ==========================================
# file system and app configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('VIEWFLOW_SECRET', 'dev-secret-key-gautham-deepak')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'viewflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max

# Markdown Filter
@app.template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ""
    # Convert markdown to HTML
    html = markdown.markdown(text)
    # Sanitize HTML
    allowed_tags = ['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'br', 'h1', 'h2', 'h3', 'blockquote', 'code', 'pre']
    allowed_attrs = {'a': ['href', 'title', 'target']}
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return clean_html

app.config['VOSK_MODEL_PATH'] = os.environ.get('VOSK_MODEL_PATH', os.path.join(UPLOAD_FOLDER, 'models', 'vosk-model-small-en-us-0.15'))

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

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
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(300), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    videos = db.relationship('Video', backref='uploader', lazy=True)

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    views = db.Column(db.Integer, default=0)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    resolutions = db.Column(db.String(200), nullable=True)  # JSON string: ["720p", "480p"]
    height = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='ready')
    heatmap = db.Column(db.Text, default='[]')
    preview_images = db.Column(db.Text, nullable=True)


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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    
    user = db.relationship('User', backref='comments', lazy=True)
    video = db.relationship('Video', backref=db.backref('comments', lazy=True, cascade="all, delete-orphan"))

class ViewHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='view_history', lazy=True)
    video = db.relationship('Video', backref='view_events', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

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

# ==========================================
# RECOMMENDATION ENGINE
# ==========================================

def get_user_profile_vector(user_id):
    """
    Builds a weighted feature vector for the user based on watch history.
    Features: Categories, Tags, Channels.
    Weights: Recency (Decay), Frequency (Replays), Context (Last 2 videos).
    """
    # Get last 50 views for long-term profile
    history = ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.timestamp.desc()).limit(50).all()
    
    if not history:
        return None

    # 1. Analyze Replays (Frequency)
    video_counts = Counter([h.video_id for h in history])
    
    # 2. Build User Profile Vector
    user_vector = defaultdict(float)
    
    # Hyperparameters
    WEIGHT_CATEGORY = 3.0
    WEIGHT_TAG = 1.0
    WEIGHT_CHANNEL = 2.0
    DECAY_FACTOR = 0.95  # 5% decay per step back in history
    
    # Short-term context (Last 2 videos) - "Current Mood"
    last_2_ids = [h.video_id for h in history[:2]]
    
    for idx, h in enumerate(history):
        if not h.video:
            continue
            
        # Time Decay: Recent views have higher weight
        recency_weight = pow(DECAY_FACTOR, idx)
        
        # Replay Multiplier: Boost if watched multiple times
        # Logarithmic scaling to prevent spamming from dominating
        replay_count = video_counts[h.video_id]
        replay_mult = 1.0 + math.log(replay_count) if replay_count > 1 else 1.0
        
        # Short-term Context Boost: Massive boost for the immediate previous videos
        context_boost = 2.5 if h.video_id in last_2_ids else 1.0
        
        # Final Event Weight
        final_weight = recency_weight * replay_mult * context_boost
        
        # Feature Extraction & Weighting
        if h.video.category:
            user_vector[f"cat:{h.video.category}"] += WEIGHT_CATEGORY * final_weight
        
        if h.video.tags:
            # tags are comma separated
            t_list = [t.strip().lower() for t in h.video.tags.split(',') if t.strip()]
            for tag in t_list:
                user_vector[f"tag:{tag}"] += WEIGHT_TAG * final_weight
                
        user_vector[f"chan:{h.video.user_id}"] += WEIGHT_CHANNEL * final_weight

    return user_vector

def get_recommendations(user_id, limit=4, exclude_video_ids=None):
    if not user_id:
        return []
    
    user_vector = get_user_profile_vector(user_id)
    
    if not user_vector:
        return []

    # Fetch candidate videos (public videos)
    query = Video.query.filter_by(is_public=True)
    
    if exclude_video_ids:
        query = query.filter(~Video.id.in_(exclude_video_ids))
    
    candidates = query.all()
    
    scored_videos = []
    for vid in candidates:
        score = 0
        
        # Dot Product: User Vector • Video Feature Vector
        
        # Category Match
        if vid.category:
            score += user_vector.get(f"cat:{vid.category}", 0)
        
        # Tag Match
        if vid.tags:
            v_tags = [t.strip().lower() for t in vid.tags.split(',') if t.strip()]
            for t in v_tags:
                score += user_vector.get(f"tag:{t}", 0)
        
        # Channel Match
        score += user_vector.get(f"chan:{vid.user_id}", 0)
        
        if score > 0:
            # Add a tiny random noise to break ties and add serendipity
            score += random.uniform(0, 0.5)
            scored_videos.append((score, vid))
            
    # Sort by score desc
    scored_videos.sort(key=lambda x: x[0], reverse=True)
    
    return [v for s, v in scored_videos[:limit]]

def get_channel_recommendation(user_id):
    user_vector = get_user_profile_vector(user_id)
    if not user_vector:
        return None, []
        
    # Extract channel scores from the vector
    channel_scores = {}
    for key, score in user_vector.items():
        if key.startswith("chan:"):
            chan_id = int(key.split(":")[1])
            channel_scores[chan_id] = score
            
    if not channel_scores:
        return None, []
        
    # Get top channel by score
    top_channel_id = max(channel_scores, key=channel_scores.get)
    channel = User.query.get(top_channel_id)
    
    if not channel:
        return None, []
    
    # Get videos from this channel
    videos = Video.query.filter_by(user_id=top_channel_id, is_public=True).order_by(Video.upload_date.desc()).limit(4).all()
    
    return channel, videos

# ==========================================
# BLUEPRINTS
# ==========================================

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

@main_bp.app_template_filter('format_date')
def format_date(date):
    if not date:
        return 'Unknown'
    return date.strftime('%b %d, %Y')

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
                if 'category' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN category VARCHAR(100)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'tags' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN tags VARCHAR(500)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'resolutions' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN resolutions VARCHAR(200)"))
                        conn.commit()
                    except Exception:
                        pass
                if 'height' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN height INTEGER"))
                        conn.commit()
                    except Exception:
                        pass
                if 'status' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN status VARCHAR(20) DEFAULT 'ready'"))
                        conn.commit()
                    except Exception:
                        pass
                if 'heatmap' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN heatmap TEXT DEFAULT '[]'"))
                        conn.commit()
                    except Exception:
                        pass
                if 'preview_images' not in video_cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN preview_images TEXT"))
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
                if 'notifications_enabled' not in user_cols:
                    try:
                        conn.execute(text("ALTER TABLE user ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1"))
                        conn.commit()
                    except Exception:
                        pass
        except Exception:
            # if inspector or engine access fails, just continue
            pass


# Initialize DB and uploads at import time so the app is ready on start
init_db()

@main_bp.route('/')
def home():
    # Base query for visible videos
    base_query = Video.query.filter_by(status='ready')
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


@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.home'))
    
    # Process natural language/voice commands
    clean_query = voice.process_command(query)
    
    # Search in video title, description, and uploader name
    search_pattern = f"%{clean_query}%"
    videos = Video.query.join(Video.uploader).filter(
        (Video.is_public == True) &
        (
            (Video.title.ilike(search_pattern)) |
            (Video.description.ilike(search_pattern)) |
            (User.username.ilike(search_pattern)) |
            (User.display_name.ilike(search_pattern))
        )
    ).order_by(Video.upload_date.desc()).all()
    
    return render_template('search.html', title=f"Search: {clean_query}", query=clean_query, videos=videos)


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

    try:
        static_ffmpeg.add_paths()
    except Exception:
        pass
    
    # Save temporary file
    unique_id = str(uuid.uuid4())
    temp_webm = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_voice_{unique_id}.webm')
    temp_wav = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_voice_{unique_id}.wav')
    
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
        model_path = app.config.get('VOSK_MODEL_PATH')
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

@main_bp.route('/test-async')
@login_required
def test_async():
    return render_template('test_async.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Login failed. Check your email and password.')
    return render_template('login.html', title="Login")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        display_name = request.form.get('display_name') or username
        email = request.form.get('email')
        password = request.form.get('password')
        dob_str = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        location = request.form.get('location')
        bio = request.form.get('bio')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('auth.register'))
        
        # Parse DOB
        date_of_birth = None
        if dob_str:
            try:
                date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Handle profile picture upload
        profile_pic_path = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                if allowed_file(file.filename, 'image'):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    save_name = f"profile_{timestamp}_{filename}"
                    
                    # Create profiles directory if it doesn't exist
                    profiles_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')
                    os.makedirs(profiles_dir, exist_ok=True)
                    
                    save_path = os.path.join(profiles_dir, save_name)
                    file.save(save_path)
                    # Force forward slash for database path to ensure URL compatibility
                    profile_pic_path = f"profiles/{save_name}"
                    print(f"[REGISTER] Saved profile picture: {save_name}")
                else:
                    flash('Invalid image file type. Allowed: jpg, jpeg, png, gif, webp')
            else:
                if file.filename:
                    print(f"[REGISTER] Profile picture rejected: {file.filename} (invalid format)")
            
        new_user = User(
            username=username,
            display_name=display_name,
            email=email, 
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            date_of_birth=date_of_birth,
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
        return redirect(url_for('main.home'))
    return render_template('register.html', title="Register")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.display_name = request.form.get('display_name')
        current_user.email = request.form.get('email')
        current_user.gender = request.form.get('gender')
        current_user.location = request.form.get('location')
        current_user.bio = request.form.get('bio')
        current_user.notifications_enabled = 'notifications_enabled' in request.form
        
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            try:
                current_user.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                if allowed_file(file.filename, 'image'):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    save_name = f"profile_{timestamp}_{filename}"
                    profiles_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')
                    os.makedirs(profiles_dir, exist_ok=True)
                    save_path = os.path.join(profiles_dir, save_name)
                    file.save(save_path)
                    current_user.profile_pic = f"profiles/{save_name}"
        
        try:
            db.session.commit()
            flash('Profile updated successfully')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile')
            
    return render_template('settings.html', title='Settings')


@main_bp.route('/subscriptions')
@login_required
def subscriptions():
    # 1. Get subscribed channels
    subs = Subscription.query.filter_by(subscriber_id=current_user.id).all()
    channel_ids = [s.channel_id for s in subs]
    
    if not channel_ids:
        return render_template('subscriptions.html', title='Subscriptions', channels=[], videos=[])

    # 2. Sort channels by engagement (view count from history)
    # Count views per channel for the current user
    view_counts = db.session.query(Video.user_id, func.count(ViewHistory.id))\
        .join(ViewHistory, ViewHistory.video_id == Video.id)\
        .filter(ViewHistory.user_id == current_user.id)\
        .filter(Video.user_id.in_(channel_ids))\
        .group_by(Video.user_id).all()
    
    engagement_map = {uid: count for uid, count in view_counts}
    
    channels = User.query.filter(User.id.in_(channel_ids)).all()
    # Sort by engagement desc
    channels.sort(key=lambda c: engagement_map.get(c.id, 0), reverse=True)
    
    # 3. Get latest videos from subscriptions
    videos = Video.query.filter(Video.user_id.in_(channel_ids), Video.is_public == True, Video.status == 'ready')\
        .order_by(Video.upload_date.desc()).limit(20).all()
        
    return render_template('subscriptions.html', title='Subscriptions', channels=channels, videos=videos)


@main_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark as read
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    return render_template('notifications.html', title='Notifications', notifications=notifs)


def transcode_video(input_path, output_path, height):
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'libx264', '-crf', '28', '-preset', 'veryfast',
            '-c:a', 'copy',
            output_path, '-y'
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print(f"Transcoding error: {e}")
        return False

def process_video_upload(app, video_id, video_path, save_name, timestamp):
    with app.app_context():
        with app.test_request_context():
            try:
                video = Video.query.get(video_id)
                if not video:
                    return

                # Generate thumbnail
                thumbnail_name = f"{timestamp}_thumb.jpg"
                thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_name)
                generate_thumbnail(video_path, thumbnail_path)
                
                # Detect original height
                original_height = 0
                try:
                    cap = cv2.VideoCapture(video_path)
                    if cap.isOpened():
                        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()
                except:
                    pass

                # Transcode
                resolutions = []
                base_name = os.path.splitext(save_name)[0]
                for res in [720, 480, 360]:
                    # Don't upscale
                    if original_height > 0 and res >= original_height:
                        continue
                        
                    res_name = f"{base_name}_{res}p.mp4"
                    res_path = os.path.join(app.config['UPLOAD_FOLDER'], res_name)
                    if transcode_video(video_path, res_path, res):
                        resolutions.append(f"{res}p")

                # Generate preview images (10 frames)
                preview_images = []
                try:
                    cap = cv2.VideoCapture(video_path)
                    if cap.isOpened():
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        if total_frames > 0:
                            for i in range(10):
                                frame_idx = int(total_frames * (i / 10))
                                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                                ret, frame = cap.read()
                                if ret:
                                    p_name = f"{timestamp}_preview_{i}.jpg"
                                    p_path = os.path.join(app.config['UPLOAD_FOLDER'], p_name)
                                    # Resize to small
                                    frame = cv2.resize(frame, (160, 90))
                                    cv2.imwrite(p_path, frame)
                                    preview_images.append(p_name)
                    cap.release()
                except Exception as e:
                    print(f"Preview generation error: {e}")

                # Update video
                video.thumbnail = thumbnail_name if os.path.exists(thumbnail_path) else None
                video.resolutions = json.dumps(resolutions) if resolutions else None
                video.height = original_height if original_height > 0 else None
                video.status = 'ready'
                video.preview_images = json.dumps(preview_images) if preview_images else None
                
                # Notify subscribers
                try:
                    subscribers = Subscription.query.filter_by(channel_id=video.user_id).all()
                    for sub in subscribers:
                        subscriber = User.query.get(sub.subscriber_id)
                        if subscriber and getattr(subscriber, 'notifications_enabled', True):
                            notif = Notification(
                                user_id=subscriber.id,
                                message=f"{video.uploader.username} uploaded: {video.title}",
                                link=url_for('main.watch', video_id=video.id)
                            )
                            db.session.add(notif)
                except Exception as e:
                    print(f"Notification error: {e}")

                db.session.commit()
                
            except Exception as e:
                print(f"Background upload error: {e}")
                if video:
                    video.status = 'failed'
                    db.session.commit()

@main_bp.route('/api/video/<int:video_id>/heatmap', methods=['GET', 'POST'])
def video_heatmap(video_id):
    video = Video.query.get_or_404(video_id)
    
    if request.method == 'POST':
        # Update heatmap
        try:
            data = request.get_json()
            bucket = int(data.get('bucket', -1))
            if 0 <= bucket < 100:
                heatmap = json.loads(video.heatmap) if video.heatmap else []
                if not heatmap or len(heatmap) != 100:
                    heatmap = [0] * 100
                heatmap[bucket] += 1
                video.heatmap = json.dumps(heatmap)
                db.session.commit()
                return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
            
    # GET
    return jsonify({'heatmap': json.loads(video.heatmap) if video.heatmap else []})

@main_bp.route('/api/upload_status')
@login_required
def upload_status():
    # Get videos that are processing
    processing = Video.query.filter_by(user_id=current_user.id, status='processing').all()
    return jsonify({
        'processing': [{'id': v.id, 'title': v.title} for v in processing]
    })

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('main.upload'))
        file = request.files['file']
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        tags = request.form.get('tags')
        
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('main.upload'))
            
        if file and allowed_file(file.filename, 'video'):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            save_name = f"{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
            file.save(video_path)
            
            # Create initial video entry
            new_video = Video(
                title=title,
                description=description,
                filename=save_name,
                user_id=current_user.id,
                category=category,
                tags=tags,
                status='processing'
            )
            db.session.add(new_video)
            db.session.commit()
            
            # Start background task
            thread = threading.Thread(target=process_video_upload, args=(app, new_video.id, video_path, save_name, timestamp))
            thread.start()

            flash('Upload started! We are processing your video in the background.')
            return redirect(url_for('main.home'))
            
    return render_template('upload.html', title="Upload")

@main_bp.route('/watch/<int:video_id>')
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
            # Record history if authenticated
            if current_user.is_authenticated:
                vh = ViewHistory(user_id=current_user.id, video_id=video.id)
                db.session.add(vh)
            db.session.commit()
            print(f"[VIEW DEBUG] Views incremented: {old_views} -> {video.views}")
        else:
            print(f"[VIEW DEBUG] Owner viewing - no increment")
    except Exception as e:
        print(f"[VIEW DEBUG] Error: {e}")
        db.session.rollback()

    # recommended: use ML engine for logged in users, else fallback
    recommended = []
    if current_user.is_authenticated:
        try:
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

    # Prepare resolutions list
    avail_resolutions = []
    if getattr(video, 'resolutions', None):
        try:
            res_list = json.loads(video.resolutions)
            base_name = os.path.splitext(video.filename)[0]
            for r in res_list:
                avail_resolutions.append({
                    'label': r,
                    'src': url_for('main.uploaded_file', filename=f"{base_name}_{r}.mp4")
                })
        except:
            pass
    
    # Add original
    orig_label = 'Original'
    if getattr(video, 'height', None):
        orig_label = f"{video.height}p"
        
    avail_resolutions.insert(0, {
        'label': orig_label,
        'src': url_for('main.uploaded_file', filename=video.filename)
    })

    return render_template('watch.html', title=video.title, video=video, recommended=recommended,
                           likes=likes, dislikes=dislikes, is_liked=is_liked, is_disliked=is_disliked,
                           is_subscribed=is_subscribed, comments=comments, resolutions=avail_resolutions)

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax')

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

@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Minimal stubs for endpoints referenced by templates originally written for a blueprint.
# These are lightweight and redirect back to home or the referrer so `url_for` works.
@main_bp.route('/user/<string:username>')
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
        videos = Video.query.filter_by(user_id=channel.id).filter(Video.status != 'failed').order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.filter_by(user_id=channel.id, is_public=True, status='ready').order_by(Video.upload_date.desc()).all()

    # compute subscribers count and whether current_user subscribes
    subs_count = Subscription.query.filter_by(channel_id=channel.id).count()
    is_subscribed = False
    if current_user and current_user.is_authenticated:
        is_subscribed = bool(Subscription.query.filter_by(channel_id=channel.id, subscriber_id=current_user.id).first())

    # Analytics data (only for owner)
    analytics_data = {}
    if current_user.is_authenticated and current_user.id == channel.id:
        # Summary Stats
        total_views = sum(v.views for v in channel.videos)
        total_subs = subs_count
        total_videos = len(channel.videos)
        
        # Charts Data (Last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Views per day
        views_daily = db.session.query(
            func.date(ViewHistory.timestamp), func.count(ViewHistory.id)
        ).join(Video).filter(
            Video.user_id == channel.id,
            ViewHistory.timestamp >= thirty_days_ago
        ).group_by(func.date(ViewHistory.timestamp)).all()
        
        # Subs per day
        subs_daily = db.session.query(
            func.date(Subscription.created_at), func.count(Subscription.id)
        ).filter(
            Subscription.channel_id == channel.id,
            Subscription.created_at >= thirty_days_ago
        ).group_by(func.date(Subscription.created_at)).all()
        
        # Format for Chart.js
        dates = [(datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
        views_data_map = {d: 0 for d in dates}
        for date_str, count in views_daily:
            if date_str in views_data_map:
                views_data_map[date_str] = count
                
        subs_data_map = {d: 0 for d in dates}
        for date_str, count in subs_daily:
            if date_str in subs_data_map:
                subs_data_map[date_str] = count
                
        # Top Videos
        top_videos = Video.query.filter_by(user_id=channel.id).order_by(Video.views.desc()).limit(5).all()

        analytics_data = {
            'total_views': total_views,
            'total_subs': total_subs,
            'total_videos': total_videos,
            'dates': dates,
            'views_data': [views_data_map[d] for d in dates],
            'subs_data': [subs_data_map[d] for d in dates],
            'top_videos': top_videos
        }

    return render_template('user.html', title=display_name_val, channel=channel, videos=videos, subs_count=subs_count, is_subscribed=is_subscribed, analytics=analytics_data)


@main_bp.route('/subscribe/<int:channel_id>', methods=['POST'])
def subscribe(channel_id):
    if not current_user.is_authenticated:
        # If AJAX request, return JSON for client to redirect to login
        if is_ajax(request):
            return jsonify({'error': 'login_required', 'redirect': url_for('auth.login')}), 401
        flash('Please sign in to subscribe')
        return redirect(url_for('auth.login'))

    channel = User.query.get_or_404(channel_id)
    # toggle subscription
    existing = Subscription.query.filter_by(channel_id=channel.id, subscriber_id=current_user.id).first()
    if existing:
        try:
            db.session.delete(existing)
            db.session.commit()
            if is_ajax(request):
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
            if is_ajax(request):
                subs_count = Subscription.query.filter_by(channel_id=channel.id).count()
                return jsonify({'subscribed': True, 'subs_count': subs_count})
        except Exception:
            db.session.rollback()
            flash('Failed to subscribe')
    # Default redirect for non-AJAX
    return redirect(url_for('main.user_profile', username=channel.username))


@main_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    # Only owner can delete
    if not (current_user.is_authenticated and current_user.id == video.user_id):
        flash('Not authorized to delete this video')
        return redirect(url_for('main.home'))

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

    return redirect(url_for('main.home'))


@main_bp.route('/video/<int:video_id>/visibility', methods=['POST'])
@login_required
def toggle_visibility(video_id):
    video = Video.query.get_or_404(video_id)
    # Only owner can change visibility
    if not (current_user.is_authenticated and current_user.id == video.user_id):
        flash('Not authorized')
        return redirect(url_for('main.home'))

    new_vis = request.form.get('visibility')
    video.is_public = True if new_vis == 'public' else False
    try:
        db.session.commit()
        flash('Visibility updated')
    except Exception:
        db.session.rollback()
        flash('Failed to update visibility')
    return redirect(url_for('main.watch', video_id=video_id))


@main_bp.route('/video/<int:video_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    if not (current_user.is_authenticated and current_user.id == video.user_id):
        flash('Not authorized')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        video.title = request.form.get('title')
        video.description = request.form.get('description')
        video.category = request.form.get('category')
        video.tags = request.form.get('tags')
        
        # Handle thumbnail update if provided
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                save_name = f"{timestamp}_thumb_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))
                video.thumbnail = save_name

        db.session.commit()
        flash('Video updated')
        return redirect(url_for('main.watch', video_id=video.id))
        
    return render_template('edit_video.html', title='Edit Video', video=video)


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
            else:
                existing.type = t
                db.session.commit()
        else:
            r = Reaction(video_id=video.id, user_id=current_user.id, type=t)
            db.session.add(r)
            db.session.commit()
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

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

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
                if 'resolutions' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN resolutions VARCHAR(200)"))
                    except Exception:
                        pass
                if 'height' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN height INTEGER"))
                    except Exception:
                        pass
                if 'status' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN status VARCHAR(20) DEFAULT 'ready'"))
                    except Exception:
                        pass
                if 'heatmap' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN heatmap TEXT DEFAULT '[]'"))
                    except Exception:
                        pass
                if 'preview_images' not in cols:
                    try:
                        conn.execute(text("ALTER TABLE video ADD COLUMN preview_images TEXT"))
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
                    if 'date_of_birth' not in user_cols:
                        try:
                            conn.execute(text("ALTER TABLE user ADD COLUMN date_of_birth DATE"))
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
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug, port=port)