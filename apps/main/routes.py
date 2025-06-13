from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from apps.courses.models import User
import os
from werkzeug.utils import secure_filename
from core.extensions import db, bcrypt

main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/main")

@main_bp.route("/")
def landing():
    return render_template("landing.html")
def health_check():
    return 'OK', 200

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    return render_template('landing.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

# Redundant route registration functions below (could be merged with above logic)
def register_routes(app):
    @app.route('/courses')
    @login_required
    def index():
        return render_template('index.html', user=current_user)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            license_number = request.form.get('license_number')
            phone = request.form.get('phone')
            photo_file = request.files.get('id_upload')

            if User.query.filter_by(email=email).first():
                flash('That email is already registered. Please log in or use a different email.', 'danger')
                return redirect(url_for('register'))

            photo_filename = None
            if photo_file and photo_file.filename:
                photo_filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.root_path, 'static/uploads', photo_filename)
                photo_file.save(photo_path)

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                license_number=license_number or None,
                phone=phone or None,
                id_upload=photo_filename
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Login failed. Check your credentials.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
