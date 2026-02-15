import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from calendar_service import get_calendar_service, create_event
from event_parser import parse_event_description

gcal_cred_path = "./gcal-event-adder-c77a1506daf4.json"
calendar_id = os.getenv('CALENDAR_ID')

def run():
    description = input("Describe the event! ")
    parsed_description = parse_event_description(description, reference_time=datetime.now(timezone.utc))
    if parsed_description.get("is_full_day"):
        start = {"date": parsed_description["start"]}
        end = {"date": parsed_description["end"]}
    else:
        start = {"dateTime": parsed_description["start"], "timeZone": "America/Los_Angeles"}
        end = {"dateTime": parsed_description["end"], "timeZone": "America/Los_Angeles"}
    event = {
        "summary": parsed_description["summary"],
        "description": parsed_description.get("description") or "",
        "location": parsed_description.get("location") or "",
        "start": start,
        "end": end,
    }
    service, gcal_id = get_calendar_service(gcal_cred_path, calendar_id or "primary")
    create_event(service, gcal_id, event)

if __name__ == "__main__":
    run()
