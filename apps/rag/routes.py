from flask import Blueprint, request, jsonify

rag_bp = Blueprint('rag', __name__)
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/rag', methods=['POST'])
def run_rag():
    from apps.rag.retriever import run_rag_pipeline
    prompt = request.json.get("prompt")
    result = run_rag_pipeline(prompt)
    return jsonify({"result": result})

@rag_bp.route('/ask', methods=['POST'])
def ask():
    from apps.rag.retriever import run_rag_pipeline
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
