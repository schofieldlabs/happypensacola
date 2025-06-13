import os
from flask import Blueprint, render_template, session, redirect, url_for, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .models import CalendarCredential, Booking
from core.extensions import db
import stripe
from .services import SERVICE_CATALOG
from datetime import datetime, timedelta, timezone, time as dt_time
from dateutil import parser
import pytz
LOCAL_TZ = pytz.timezone('America/Chicago')


# Below is Jessica and Ralph's general availability, which is used to determine available slots for booking.
# This availability is further limited by the specific service type and the owner's calendar events.

# Days 0 through 4 represent Monday through Friday, and 5 and 6 represent Saturday and Sunday.
# Each tuple represents a time range in 24-hour format (start_hour, end_hour).

# Ralph is available from 12 PM to 1 PM and 5 PM to 9 PM on weekdays, and all day on weekends.
# Jessica is available all day from 7 AM to 8 PM on all days except Sunday, when she is not available.

RALPH_AVAILABILITY = {
    0: [(12, 13), (17, 21)],
    1: [(12, 13), (17, 21)],
    2: [(12, 13), (17, 21)],
    3: [(12, 13), (17, 21)],
    4: [(12, 13), (17, 21)],
    5: [(7, 20)],
    6: [(7, 20)],
}

JESSICA_AVAILABILITY = {
    0: [(7, 20)],
    1: [(7, 20)],
    2: [(7, 20)],
    3: [(7, 20)],
    4: [(7, 20)],
    5: [(7, 20)],
}

OWNER_AVAILABILITIES = {
    'ralph': RALPH_AVAILABILITY,
    'jessica': JESSICA_AVAILABILITY,
}

calendar_routes = Blueprint('calendar_routes', __name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # This gives you apps/main/
SECRETS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'etc', 'secrets'))

CLIENT_SECRETS_FILE = os.path.join(SECRETS_DIR, 'credentials.json')
JESSICA_CLIENT_SECRETS_FILE = os.path.join(SECRETS_DIR, 'jessica_credentials.json')

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
    session[f'{owner}_state'] = state
    return redirect(authorization_url)

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

    # 🚀 SUPER DEBUGGER START 🚀
    print("====== GOOGLE CREDENTIALS RECEIVED ======")
    print(f"Token: {creds.token}")
    print(f"Refresh Token: {creds.refresh_token}")
    print(f"Token URI: {creds.token_uri}")
    print(f"Client ID: {creds.client_id}")
    print(f"Client Secret: {creds.client_secret}")
    print(f"Scopes: {creds.scopes}")
    print("==========================================")
    # 🚀 SUPER DEBUGGER END 🚀

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

    start_dt = datetime.fromisoformat(data['slot']).astimezone(timezone.utc)
    end_dt = start_dt + timedelta(minutes=config['duration'])

    event = {
        'summary': config['name'],
        'description': f"Client: {data['name']}, Email: {data['email']}, Phone: {data['phone']}",
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'},
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

# === Availability Logic with timezone patch ===

def get_available_slots(service_type):
    config = SERVICE_CATALOG[service_type]
    owner = config['owner']
    duration = config['duration']
    days_ahead = config['days_ahead']
    hour = config['hours']

    creds = load_credentials(owner)
    service = build('calendar', 'v3', credentials=creds)
    weekly_available_days = OWNER_AVAILABILITIES.get(owner, {})

    now = datetime.now(LOCAL_TZ)
    end_date = now + timedelta(days=days_ahead)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.astimezone(timezone.utc).isoformat(),
        timeMax=end_date.astimezone(timezone.utc).isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    slots = []
    for day_offset in range(days_ahead):
        date = now.date() + timedelta(days=day_offset)
        weekday = date.weekday()
        if weekday not in weekly_available_days:
            continue
        for start_hour, end_hour in weekly_available_days[weekday]:
            for hour in range (start_hour, end_hour):
                slot_time = LOCAL_TZ.localize(datetime.combine(date, dt_time(hour, 0)))
                conflict = any(
                    (slot_time >= parse_event(e['start']) and slot_time < parse_event(e['end']))
                    for e in events
                )
                if not conflict and slot_time > now:
                    slots.append(slot_time)
    return slots

def parse_event(event_time):
    if 'dateTime' in event_time:
        dt = parser.isoparse(event_time['dateTime'])
    else:
        dt = parser.isoparse(event_time['date'])
    return dt.astimezone(LOCAL_TZ)

# === Credentials Storage ===

def get_secrets_file(owner):
    return CLIENT_SECRETS_FILE if owner == 'ralph' else JESSICA_CLIENT_SECRETS_FILE

def store_credentials(owner, creds):
    missing = []
    if not creds.refresh_token:
        missing.append("refresh_token")
    if not creds.token_uri:
        missing.append("token_uri")
    if not creds.client_id:
        missing.append("client_id")
    if not creds.client_secret:
        missing.append("client_secret")

    if missing:
        print(f"[OAuth Debug] Incomplete credentials received for {owner}: missing {', '.join(missing)}")
        return f"OAuth authorization failed: missing fields: {', '.join(missing)}", 500

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

    return f"{owner.title()}'s calendar successfully authorized!"

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