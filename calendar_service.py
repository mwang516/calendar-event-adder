from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials_path = "./gcal-event-adder-c77a1506daf4.json"

def get_calendar_service(credentials_path: str, calendar_id: str):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=credentials)
    return (service, calendar_id)



def create_event(service, calendar_id: str, event: dict):
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (created_event.get('htmlLink')))
