from flask import Blueprint, render_template

wellness_bp = Blueprint('wellness', __name__)

@wellness_bp.route('/wellness')
def index(): 
    return render_template('wellness/index.html') 