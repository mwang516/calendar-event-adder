import json
from datetime import datetime
from openai import OpenAI

client = OpenAI()

EVENT_PARSER_PROMPT = "Parse the event description into JSON with: summary, description (optional), location (optional), start, end, is_full_day (boolean). For timed events use ISO8601 for start/end. For full-day use YYYY-MM-DD, end is exclusive (e.g. 1-day event: start 2025-02-15, end 2025-02-16). Use the current datetime to resolve relative references like 'tomorrow', 'next Tuesday', 'in 2 hours'. For location: expand vague names (e.g. 'Starbucks' → 'Starbucks, [full address]') into a format Google Calendar/Maps can interpret—prefer full street address when inferable, or 'Place Name, City' when not. Return only valid JSON, no markdown or other text."

def parse_event_description(description: str, reference_time: datetime) -> dict:
    ref = reference_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    instructions = f"The current date and time is {ref} (UTC). {EVENT_PARSER_PROMPT}"
    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=description,
        max_output_tokens=4000,
        reasoning={"effort": "low"},
    )
    return json.loads(response.output_text)
