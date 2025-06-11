
from flask import Blueprint, render_template

calendar_routes = Blueprint('calendar_routes', __name__)

@calendar_routes.route('/book-mediation')
def book_mediation():
    return render_template('booking/mediation.html')  # Make sure this template exists

@calendar_routes.route('/book-wellness')
def book_wellness():
    return render_template('booking/wellness.html')  # Make sure this template exists
