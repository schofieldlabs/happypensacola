# apps/rag/__init__.py

from flask import Blueprint

rag_bp = Blueprint('rag', __name__)

from . import routes
