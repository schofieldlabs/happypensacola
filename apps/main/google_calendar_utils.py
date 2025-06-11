import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_upcoming_events(creds_dict, max_results=10):
    creds = Credentials(**creds_dict)
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events

def get_free_busy(creds_dict, start_time, end_time):
    creds = Credentials(**creds_dict)
    service = build('calendar', 'v3', credentials=creds)
    body = {
        "timeMin": start_time.isoformat() + 'Z',
        "timeMax": end_time.isoformat() + 'Z',
        "timeZone": 'UTC',
        "items": [{"id": 'primary'}]
    }
    response = service.freebusy().query(body=body).execute()
    busy_times = response['calendars']['primary']['busy']
    return busy_times
