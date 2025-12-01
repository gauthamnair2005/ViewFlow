import os
from flask import Flask
from models import db
from flask_login import LoginManager

__version__ = '0.5.4'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('VIEWFLOW_SECRET', 'dev-secret-key-gautham-deepak')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'viewflow.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    # user loader for flask-login
    try:
        from models import User

        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception:
                return None
    except Exception:
        pass

    from auth import auth_bp
    from views import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Try to bundle Video.js locally for offline/dev use
    def _ensure_videojs_local():
        try:
            import urllib.request
            static_vendor = os.path.join(app.static_folder, 'vendor')
            os.makedirs(static_vendor, exist_ok=True)
            js_path = os.path.join(static_vendor, 'video.min.js')
            css_path = os.path.join(static_vendor, 'video-js.css')
            have = True
            if not os.path.exists(js_path):
                try:
                    urllib.request.urlretrieve('https://vjs.zencdn.net/8.20.0/video.min.js', js_path)
                except Exception:
                    have = False
            if not os.path.exists(css_path):
                try:
                    urllib.request.urlretrieve('https://vjs.zencdn.net/8.20.0/video-js.css', css_path)
                except Exception:
                    have = False
            app.config['VIDEOJS_LOCAL'] = have and os.path.exists(js_path) and os.path.exists(css_path)
        except Exception:
            app.config['VIDEOJS_LOCAL'] = False

    _ensure_videojs_local()

    # Create DB and try to add new columns if older DB exists
    with app.app_context():
        db.create_all()
        # If the users table exists but missing columns, try to add them (SQLite supports ADD COLUMN)
        try:
            from models import User
            # pragma: check columns
            from sqlalchemy import text
            conn = db.engine.connect()
            cols = conn.execute(text("PRAGMA table_info('user')")).fetchall()
            col_names = {c[1] for c in cols}
            if 'display_name' not in col_names:
                conn.execute(text("ALTER TABLE user ADD COLUMN display_name TEXT"))
            if 'age' not in col_names:
                conn.execute(text("ALTER TABLE user ADD COLUMN age INTEGER"))
            # Check video table for thumbnail column
            try:
                vcols = conn.execute(text("PRAGMA table_info('video')")).fetchall()
                vcol_names = {c[1] for c in vcols}
                if 'thumbnail' not in vcol_names:
                    conn.execute(text("ALTER TABLE video ADD COLUMN thumbnail TEXT"))
            except Exception:
                pass
            conn.close()
        except Exception:
            pass

    return app
