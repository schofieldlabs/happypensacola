from flask import Blueprint, render_template

ministry_bp = Blueprint('ministry', __name__)

@ministry_bp.route('/ministry')
def index(): 
    return render_template('ministry/index.html')