
# apps/main/__init__.py

from flask import Blueprint
from . import routes 
from .routes import main_bp, auth_bp
from .calendar_routes import calendar_routes


# This file ensures your blueprints are available when the main app imports this module.
# It's already sufficient if you're importing `main_bp` and `auth_bp` into `run.py` or elsewhere.
# No need to redefine anything else here.

# main_bp = Blueprint("main", __name__, template_folder="templates")


__all__ = ['main_bp', 'auth_bp']
