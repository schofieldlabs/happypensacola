import os
import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .models import db, CalendarCredential

calendar_routes = Blueprint('calendar_routes', __name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRETS_FILE = 'credentials.json'
JESSICA_CLIENT_SECRETS_FILE = 'jessica_credentials.json'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# === Admin OAuth Routes ===

@calendar_routes.route('/authorize/<owner>', endpoint='authorize')
def authorize(owner):
    secrets = get_secrets_file(owner)
    flow = Flow.from_client_secrets_file(
        secrets, scopes=SCOPES,
        redirect_uri=url_for('calendar_routes.oauth2callback', owner=owner, _external=True)
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session[f'{owner}_state'] = state
    return redirect(authorization_url)

@calendar_routes.route('/oauth2callback/<owner>', endpoint='oauth2callback')
def oauth2callback(owner):
    print(f"Received OAuth callback for {owner}")
    secrets = get_secrets_file(owner)
    state = session.get(f'{owner}_state')
    flow = Flow.from_client_secrets_file(
        secrets, scopes=SCOPES, state=state,
        redirect_uri=url_for('calendar_routes.oauth2callback', owner=owner, _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    store_credentials(owner, creds)
    return redirect(url_for(f'calendar_routes.book_{owner}'))

# === Public Booking Pages ===

@calendar_routes.route('/book-mediation', endpoint='book_ralph')
def book_mediation():
    creds = load_credentials('ralph')
    if not creds:
        return redirect(url_for('calendar_routes.authorize', owner='ralph'))

    events = get_upcoming_events(creds)
    return render_template('booking/mediation.html', events=events)

@calendar_routes.route('/book-wellness', endpoint='book_jessica')
def book_wellness():
    creds = load_credentials('jessica')
    if not creds:
        return redirect(url_for('calendar_routes.authorize', owner='jessica'))

    events = get_upcoming_events(creds)
    return render_template('booking/wellness.html', events=events)

# === Utility Functions ===

def get_secrets_file(owner):
    return CLIENT_SECRETS_FILE if owner == 'ralph' else JESSICA_CLIENT_SECRETS_FILE

def store_credentials(owner, creds):
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

def get_upcoming_events(creds, max_results=5):
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])
