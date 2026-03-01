import json
from datetime import datetime
from openai import OpenAI

client = OpenAI()

EVENT_PARSER_PROMPT = "Parse the event description into JSON with: summary, description (optional), location (optional), start, end, is_full_day (boolean). For timed events use ISO8601 for start/end in Pacific time (America/Los_Angeles). Use format YYYY-MM-DDTHH:MM:SS with NO timezone suffix (no Z, no offset). For example, 5 PM Pacific is 2026-02-15T17:00:00. For full-day use YYYY-MM-DD, end is exclusive. Use the current datetime to resolve relative references like 'tomorrow', 'next Tuesday', 'in 2 hours'. For location: expand vague names into a format Google Calendar/Maps can interpret. Return only valid JSON, no markdown or other text."

def parse_event_description(description: str, reference_time: datetime) -> dict:
    ref = reference_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    instructions = f"The current date and time is {ref} (Pacific). Interpret all user-specified times (e.g. '5pm', '8pm') as Pacific time. {EVENT_PARSER_PROMPT}"
    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=description,
        max_output_tokens=4000,
        reasoning={"effort": "low"},
    )
    return json.loads(response.output_text)
