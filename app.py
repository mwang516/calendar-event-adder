import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

from calendar_service import get_calendar_service, create_event, parsed_to_event
from event_parser import parse_event_description

app = Flask(__name__)
gcal_cred_path = "./gcal-event-adder-c77a1506daf4.json"
calendar_id = os.getenv("CALENDAR_ID")


def format_duration(start: str, end: str, is_full_day: bool) -> str:
    def fmt_time(dt: datetime) -> str:
        h = dt.hour % 12 or 12
        return f"{h}:{dt.minute:02d} {'AM' if dt.hour < 12 else 'PM'}"

    if is_full_day:
        dt = datetime.strptime(start, "%Y-%m-%d")
        return dt.strftime("%a, %b ") + str(dt.day) + dt.strftime(", %Y")
    start_dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_dt = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
    if start_dt.date() == end_dt.date():
        return f"{start_dt.strftime('%a, %b ')}{start_dt.day}{start_dt.strftime(', %Y at ')}{fmt_time(start_dt)} – {fmt_time(end_dt)}"
    return f"{start_dt.strftime('%a, %b ')}{start_dt.day}{start_dt.strftime(' at ')}{fmt_time(start_dt)} – {end_dt.strftime('%a, %b ')}{end_dt.day}{end_dt.strftime(' at ')}{fmt_time(end_dt)}"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.form.get("action") == "parse":
        description = request.form.get("description", "")
        if not description.strip():
            return render_template("index.html", error="Please enter a description.")
        parsed = parse_event_description(description.strip(), reference_time=datetime.now(ZoneInfo("America/Los_Angeles")))
        preview = {
            "summary": parsed["summary"],
            "start": parsed["start"],
            "end": parsed["end"],
            "duration_display": format_duration(
                parsed["start"], parsed["end"], parsed.get("is_full_day", False)
            ),
            "location": parsed.get("location") or "(no location)",
            "is_full_day": parsed.get("is_full_day", False),
            "description": parsed.get("description") or "",
        }
        return render_template(
            "index.html",
            description=description,
            preview=preview,
            parsed_json=parsed,
        )

    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return redirect(url_for("index"))
    summary = request.form.get("summary")
    start = request.form.get("start")
    end = request.form.get("end")
    location = request.form.get("location") or ""
    description = request.form.get("description") or ""
    is_full_day = request.form.get("is_full_day") == "1"

    if not summary or not start or not end:
        return render_template("index.html", error="Missing event data.")

    parsed = {
        "summary": summary,
        "start": start,
        "end": end,
        "location": location,
        "description": description,
        "is_full_day": is_full_day,
    }
    event = parsed_to_event(parsed)
    service, gcal_id = get_calendar_service(gcal_cred_path, calendar_id or "primary")
    create_event(service, gcal_id, event)
    return render_template("index.html", success=True)