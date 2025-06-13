from flask import Blueprint, request, jsonify
from apps.rag.retriever import run_rag_pipeline

rag_bp = Blueprint('rag', __name__)

@rag_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'Missing question'}), 400

    try:
        answer = run_rag_pipeline(question)
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"Error during RAG pipeline: {e}")
        return jsonify({'error': str(e)}), 500
