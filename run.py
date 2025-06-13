import os
from flask import Flask, send_from_directory
from config import Config
from flask_cors import CORS
from core.extensions import db, bcrypt, login_manager, migrate
from flask_login import current_user
from apps.courses.models import User
from apps.main.routes import main_bp, auth_bp
from apps.main.calendar_routes import calendar_routes
from apps.health.routes import health_bp
from apps.courses.routes import courses_bp
from apps.legal.routes import legal_bp
from apps.ministry.routes import ministry_bp
from apps.realestate.routes import realestate_bp
from apps.wellness.routes import wellness_bp
from apps.rag.routes import rag_bp, admin_bp

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_routes)
    app.register_blueprint(health_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(ministry_bp)
    app.register_blueprint(realestate_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(rag_bp, url_prefix='/rag')
    app.register_blueprint(admin_bp)

    @app.route('/rag')
    def serve_index():
        return send_from_directory('frontend', 'rag_chat.html')

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

# Render needs this:
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
