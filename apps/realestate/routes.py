from flask import Blueprint, render_template

realestate_bp = Blueprint('realestate', __name__)

@realestate_bp.route('/realestate')
def index(): 
    return render_template('realestate/index.html')