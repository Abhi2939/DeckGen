import os
import json
from schemas import ExtractedFacts
from dotenv import load_dotenv

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



