# apps/rag/admin_routes.py

from flask import Blueprint, request, render_template
from apps.rag.retriever import run_rag_pipeline

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/ingest', methods=['GET', 'POST'])
def ingest_file():
    if request.method == 'POST':
        file = request.files['file']
        path = f"docs/{file.filename}"
        file.save(path)
        run_rag_pipeline(path)
        return "Ingestion complete."
    return render_template('admin_ingest.html')
