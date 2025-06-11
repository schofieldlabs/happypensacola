from flask import Blueprint, Flask
from .routes import courses_bp
from .models import db
from .extensions import db
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

def create_app():
    bp = Blueprint("courses", __name__, template_folder="templates", static_folder="static")

    app = Flask(__name__)
#    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    db.init_app(app)
    app.register_blueprint(courses_bp, url_prefix='/courses')

    return app


from flask import Blueprint 
from . import routes 
from .routes import courses_bp
courses_bp = Blueprint("courses", __name__, template_folder="templates/courses", static_folder="static/courses")
