# app.py

from flask import Flask
from dotenv import load_dotenv
import os

from apps.courses.extensions import db, bcrypt, login_manager, migrate
from apps.courses.routes import register_routes
from apps.courses.models import User

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") or 'postgresql://postgres:Rsjs82!!@localhost/courses'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    register_routes(app)

    return app
