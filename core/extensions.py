from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()
migrate = Migrate()
