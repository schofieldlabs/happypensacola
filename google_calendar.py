import os
import datetime
from flask import Flask, session, redirect, url_for, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRETS_FILE = 'credentials.json'
JESSICA_CLIENT_SECRETS_FILE = 'jessica_credentials.json'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')  # Dev fallback

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=5, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    output = '<h2>Upcoming Events (Your Calendar)</h2>'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        output += f'<p>{start} - {event["summary"]}</p>'
    return output

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True))
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state,
        redirect_uri=url_for('oauth2callback', _external=True))
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session['credentials'] = creds_to_dict(creds)
    return redirect(url_for('index'))

# === JESSICA'S FLOW ===
@app.route('/authorize_jessica')
def authorize_jessica():
    flow = Flow.from_client_secrets_file(
        JESSICA_CLIENT_SECRETS_FILE, scopes=SCOPES,
        redirect_uri=url_for('oauth2callback_jessica', _external=True))
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['jessica_state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback_jessica')
def oauth2callback_jessica():
    state = session.get('jessica_state')
    flow = Flow.from_client_secrets_file(
        JESSICA_CLIENT_SECRETS_FILE, scopes=SCOPES, state=state,
        redirect_uri=url_for('oauth2callback_jessica', _external=True))
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session['jessica_credentials'] = creds_to_dict(creds)
    return "<h3>Jessica's calendar has been connected successfully!</h3>"

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
