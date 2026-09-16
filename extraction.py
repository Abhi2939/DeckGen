import os
import json
from schemas import ExtractedFacts
from dotenv import load_dotenv

from groq import Groq

load_dotenv()

EXTRACTION_PROMPT = """
You are extracting structured facts from a company \
description for a pitch-deck generator. Read the text below and return ONLY \
a JSON object matching this shape -- omit any field you cannot find evidence \
for in the text, don't invent numbers:

{{
  "company_name": "string",
  "one_liner": "string or null",
  "ask_amount": "string or null, e.g. '₹14 Cr'",
  "allocation": [{{"label": "string", "percent": number}}] or null,
  "process_steps": [{{"title": "string", "description": "string"}}] or null
}}

TEXT:
{text}

Return only the JSON object, no other text.
"""

def extract_facts(raw_text: str) -> ExtractedFacts:

    api_key = os.environ.get("GROQ_API_KEY")

    if api_key:
        return _extract_via_api(raw_text,api_key)
    return _mock_extract(raw_text)


def _extract_via_api(raw_text: str,api_key: str) -> ExtractedFacts:

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=raw_text)}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    data = json.loads(completion.choices[0].message.content)
    return ExtractedFacts.model_validate(data)

def _mock_extract(raw_text: str) -> ExtractedFacts:

    return ExtractedFacts(
        company_name = "Example Co",
        one_liner="A mock extraction result for pipeline testing.",
        ask_amount="₹14 Cr",
        allocation=[
            {"label": "Contingency / Buffer", "percent": 60.0},
            {"label": "Team", "percent": 20.0},
            {"label": "Marketing", "percent": 12.0},
            {"label": "Direct expenses", "percent": 5.0},
            {"label": "Capex", "percent": 3.0},
        ],

        process_steps=[
            {"title": "Onboarding", "description": "Customer signs up via app with eKYC."},
            {"title": "Verification", "description": "Real-time authentication check."},
            {"title": "Transaction", "description": "Completed within seconds."},
            {"title": "Sync", "description": "Data synced with analytics engine."},
        ],
    )