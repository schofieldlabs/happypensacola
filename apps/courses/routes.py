# routes.py
from core.models import User
from core.extensions import db, bcrypt
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
from apps.courses.models import User
from apps.courses.extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from flask import current_app as app


# Register routes for the courses module
def register_routes(app):

    @app.route('/courses')
    @login_required
    def index():
        return render_template('courses/index.html', user=current_user)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            license_number = request.form.get('license_number')
            phone = request.form.get('phone')
            photo_file = request.files.get('id_upload')

            # Check if email is already in use
            if User.query.filter_by(email=email).first():
                flash('That email is already registered. Please log in or use a different email.', 'danger')
                return redirect(url_for('register'))

            # Save photo if uploaded
            photo_filename = None
            if photo_file and photo_file.filename:
                photo_filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.root_path, 'static/uploads', photo_filename)
                photo_file.save(photo_path)

            # Create new user
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



courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses')
def index():
    return render_template('courses/index.html')
