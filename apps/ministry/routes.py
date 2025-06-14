from flask import Blueprint, render_template, request, jsonify, current_app
from apps.utils.feature_flags import ai_enabled

ministry_bp = Blueprint('ministry', __name__)

@ministry_bp.route('/ministry')
def index(): 
    return render_template('ministry/index.html')

ministry_bp = Blueprint("ministry", __name__)

@ministry_bp.route("/")
def index():
    return render_template("index.html")

@ministry_bp.route("/ai-example", methods=["POST"])
def ai_example():
    if not ai_enabled():
        return jsonify({"error": "AI features disabled"}), 503

    # Lazy load heavy AI modules
    import langchain
    import transformers
    import torch
    import ollama
    import sentence_transformers
    import langchain_community
    import langchain_core
    from sentence_transformers import SentenceTransformer


    # dummy response for now
    return jsonify({"message": "AI module loaded successfully!"})
