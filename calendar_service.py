import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service(credentials_path: str, calendar_id: str):
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=SCOPES
        )
    else:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )
    service = build('calendar', 'v3', credentials=credentials)
    return (service, calendar_id)



def parsed_to_event(parsed: dict) -> dict:
    if parsed.get("is_full_day"):
        start = {"date": parsed["start"]}
        end = {"date": parsed["end"]}
    else:
        start = {"dateTime": parsed["start"], "timeZone": "America/Los_Angeles"}
        end = {"dateTime": parsed["end"], "timeZone": "America/Los_Angeles"}
    return {
        "summary": parsed["summary"],
        "description": parsed.get("description") or "",
        "location": parsed.get("location") or "",
        "start": start,
        "end": end,
    }


def create_event(service, calendar_id: str, event: dict):
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (created_event.get('htmlLink')))
