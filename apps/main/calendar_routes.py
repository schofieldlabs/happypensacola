import os
import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .models import db, CalendarCredential, Booking
import stripe
from .services import SERVICE_CATALOG

calendar_routes = Blueprint('calendar_routes', __name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = '/etc/secrets/credentials.json'
JESSICA_CLIENT_SECRETS_FILE = '/etc/secrets/jessica_credentials.json'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# === Admin OAuth Authorization ===

@calendar_routes.route('/authorize/<owner>', endpoint='authorize')
def authorize(owner):
    secrets = get_secrets_file(owner)
    flow = Flow.from_client_secrets_file(
        secrets, scopes=SCOPES,
        redirect_uri=url_for('calendar_routes.oauth2callback', owner=owner, _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

@calendar_routes.route('/oauth2callback/<owner>', endpoint='oauth2callback')
def oauth2callback(owner):
    secrets = get_secrets_file(owner)
    state = session.get(f'{owner}_state')
    flow = Flow.from_client_secrets_file(
        secrets, scopes=SCOPES, state=state,
        redirect_uri=url_for('calendar_routes.oauth2callback', owner=owner, _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    store_credentials(owner, creds)
    return f"{owner.title()}'s calendar successfully authorized!"

# === Client Dynamic Booking Routes ===

@calendar_routes.route('/book/<service_type>', endpoint='book_service')
def book_service(service_type):
    if service_type not in SERVICE_CATALOG:
        return "Invalid service", 404

    slots = get_available_slots(service_type)
    return render_template('booking/book.html', service_type=service_type, service_name=SERVICE_CATALOG[service_type]['name'], slots=slots)

@calendar_routes.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    service_type = request.form['service_type']
    config = SERVICE_CATALOG[service_type]
    owner = config['owner']
    price = config['price']

    slot = request.form['slot']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    session['booking_data'] = {
        'service_type': service_type,
        'owner': owner,
        'slot': slot,
        'name': name,
        'email': email,
        'phone': phone
    }

    session_obj = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': config['name']},
                'unit_amount': price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('calendar_routes.booking_success', _external=True),
        cancel_url=url_for('calendar_routes.book_service', service_type=service_type, _external=True),
    )

    return redirect(session_obj.url)

@calendar_routes.route('/booking-success')
def booking_success():
    data = session.get('booking_data')
    if not data:
        return "Session expired."

    config = SERVICE_CATALOG[data['service_type']]
    creds = load_credentials(config['owner'])
    service = build('calendar', 'v3', credentials=creds)

    start_dt = datetime.datetime.fromisoformat(data['slot'])
    end_dt = start_dt + datetime.timedelta(minutes=config['duration'])

    event = {
        'summary': config['name'],
        'description': f"Client: {data['name']}, Email: {data['email']}, Phone: {data['phone']}",
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'America/Chicago'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'America/Chicago'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()

    new_booking = Booking(
        service_type=data['service_type'],
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        appointment_time=start_dt,
        google_event_id=created_event['id'],
        stripe_payment_id='TBD'
    )
    db.session.add(new_booking)
    db.session.commit()

    return "Booking complete!"

# === Availability Logic ===

def get_available_slots(service_type):
    config = SERVICE_CATALOG[service_type]
    owner = config['owner']
    duration = config['duration']
    days_ahead = config['days_ahead']
    hours = config['hours']

    creds = load_credentials(owner)
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow()
    end_date = now + datetime.timedelta(days=days_ahead)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=end_date.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    slots = []
    for day_offset in range(days_ahead):
        date = now.date() + datetime.timedelta(days=day_offset)
        for hour in hours:
            slot_time = datetime.datetime.combine(date, datetime.time(hour, 0))
            conflict = any(
                (slot_time >= parse_event(e['start']) and slot_time < parse_event(e['end']))
                for e in events
            )
            if not conflict and slot_time > now:
                slots.append(slot_time)
    return slots

def parse_event(event_time):
    if 'dateTime' in event_time:
        return datetime.datetime.fromisoformat(event_time['dateTime'].replace('Z', '+00:00'))
    else:
        return datetime.datetime.fromisoformat(event_time['date'])

# === Credentials Storage ===

def get_secrets_file(owner):
    return CLIENT_SECRETS_FILE if owner == 'ralph' else JESSICA_CLIENT_SECRETS_FILE

def store_credentials(owner, creds):
    required_fields = [creds.refresh_token, creds.token_uri, creds.client_id, creds.client_secret]
    if not all(required_fields):
        raise ValueError("OAuth credentials incomplete. Please reauthorize with full consent.")

    existing = CalendarCredential.query.filter_by(owner=owner).first()
    if not existing:
        existing = CalendarCredential(owner=owner)
    existing.token = creds.token
    existing.refresh_token = creds.refresh_token
    existing.token_uri = creds.token_uri
    existing.client_id = creds.client_id
    existing.client_secret = creds.client_secret
    existing.scopes = ",".join(creds.scopes)
    db.session.add(existing)
    db.session.commit()

def load_credentials(owner):
    record = CalendarCredential.query.filter_by(owner=owner).first()
    if not record:
        return None
    creds = Credentials(
        token=record.token,
        refresh_token=record.refresh_token,
        token_uri=record.token_uri,
        client_id=record.client_id,
        client_secret=record.client_secret,
        scopes=record.scopes.split(",")
    )
    return creds
