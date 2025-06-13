
from core.extensions import db, login_manager, bcrypt
from flask import Flask
from flask_login import LoginManager
from config import Config
from apps.main.routes import main_bp
from apps.health.routes import health_bp
from apps.courses.routes import courses_bp
from apps.main.routes import auth_bp
from apps.legal.routes import legal_bp
from apps.main.calendar_routes import calendar_routes
from apps.ministry.routes import ministry_bp
from apps.realestate.routes import realestate_bp
from apps.wellness.routes import wellness_bp
from flask_login import current_user
from apps.courses.models import User
from flask_migrate import Migrate
import os
from apps.main.models import db
from apps.main.calendar_routes import calendar_routes
from dotenv import load_dotenv

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///happy_pensacola.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_routes)
    app.register_blueprint(legal_bp)
    app.register_blueprint(ministry_bp)
    app.register_blueprint(realestate_bp)
    app.register_blueprint(wellness_bp)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Add context processor for current_user
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)