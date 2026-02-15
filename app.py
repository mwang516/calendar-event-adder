import os
from datetime import datetime, timezone
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

from calendar_service import get_calendar_service, create_event, parsed_to_event
from event_parser import parse_event_description

app = Flask(__name__)
gcal_cred_path = "./gcal-event-adder-c77a1506daf4.json"
calendar_id = os.getenv("CALENDAR_ID")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.form.get("action") == "parse":
        description = request.form.get("description", "")
        if not description.strip():
            return render_template("index.html", error="Please enter a description.")
        parsed = parse_event_description(description.strip(), reference_time=datetime.now(timezone.utc))
        preview = {
            "summary": parsed["summary"],
            "start": parsed["start"],
            "end": parsed["end"],
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