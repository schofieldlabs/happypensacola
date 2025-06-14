import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv
load_dotenv()


from config import Config
from flask_cors import CORS
from core.extensions import db, bcrypt, login_manager, migrate
from flask_login import current_user


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app)
#    app.config.from_object(Config)
    app.config['AI_FEATURE_ENABLED'] = os.getenv('AI_FEATURE_ENABLED', 'false').lower() == 'true'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if app.config.get("AI_FEATURE_ENABLED", False):
        from apps.rag.admin_routes import admin_bp
        from apps.rag.routes import rag_bp
        app.register_blueprint(admin_bp)
        app.register_blueprint(rag_bp, url_prefix='/rag')
        app.register_blueprint(admin_bp)
        @app.route('/rag')
        def serve_index():
            return send_from_directory('../frontend', 'rag_chat.html')


    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from apps.courses.models import User
    from apps.main.routes import main_bp, auth_bp
    from apps.main.calendar_routes import calendar_routes
    from apps.health.routes import health_bp
    from apps.courses.routes import courses_bp
    from apps.legal.routes import legal_bp
    from apps.ministry.routes import ministry_bp
    from apps.realestate.routes import realestate_bp
    from apps.wellness.routes import wellness_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_routes)
    app.register_blueprint(health_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(ministry_bp)
    app.register_blueprint(realestate_bp)
    app.register_blueprint(wellness_bp)

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
