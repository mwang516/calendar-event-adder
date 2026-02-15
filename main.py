import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from calendar_service import get_calendar_service, create_event, parsed_to_event
from event_parser import parse_event_description

gcal_cred_path = "./gcal-event-adder-c77a1506daf4.json"
calendar_id = os.getenv('CALENDAR_ID')

def run():
    description = input("Describe the event! ")
    parsed_description = parse_event_description(description, reference_time=datetime.now(timezone.utc))
    event = parsed_to_event(parsed_description)
    start_display = parsed_description.get("start")
    end_display = parsed_description.get("end")
    location_display = parsed_description.get("location") or "(no location)"
    print(f"\n{parsed_description['summary']}")
    print(f"  {start_display} – {end_display}")
    print(f"  {location_display}\n")
    if input("Create this event? (y/n) ").strip().lower() != "y":
        print("Cancelled.")
        return
    service, gcal_id = get_calendar_service(gcal_cred_path, calendar_id)
    create_event(service, gcal_id, event)

if __name__ == "__main__":
    run()
