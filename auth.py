import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


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
    return render_template('login.html', title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
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

        # Check if email or username already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('auth.register'))

        # Handle profile picture upload
        profile_pic_path = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                if allowed_image_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    save_name = f"profile_{timestamp}_{filename}"
                    
                    # Create profiles directory if it doesn't exist
                    profiles_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
                    os.makedirs(profiles_dir, exist_ok=True)
                    
                    save_path = os.path.join(profiles_dir, save_name)
                    file.save(save_path)
                    # Force forward slash for database path to ensure URL compatibility
                    profile_pic_path = f"profiles/{save_name}"
                else:
                    flash('Invalid image file type. Allowed: jpg, jpeg, png, gif, webp')

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
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
