import os
import json
from schemas import ExtractedFacts
from dotenv import load_dotenv

load_dotenv()

EXTRACTION_PROMPT = """
You are extracting structured facts from a company \
description for a pitch-deck generator. Read the text below and return ONLY \
a JSON object matching this shape -- omit any field you cannot find evidence \
for in the text, don't invent numbers, names or percentages:

{{
  "company_name": "string",
  "one_liner": "string or null",
  "tagline": "short slogan for the 'How it works' slide, or null",
  "ask_amount": "string or null, e.g. '₹14 Cr'",
  "allocation": [{{"label": "string", "percent": number}}] or null,
  "process_steps": [{{"title": "string", "description": "string"}}] or null,
  "market": {{
    "title": "e.g. 'Global FinTech Market'",
    "cagr": "string e.g. '15.27%' or null",
    "start": {{"year": number, "value": "e.g. 'USD 320.81 Bn'"}} or null,
    "end": {{"year": number, "value": "e.g. 'USD 652.80 Bn'"}} or null,
    "segments": [{{
      "category": "e.g. 'Service'",
      "leader_text": "e.g. 'Digital payments lead'",
      "leader_value": "e.g. '46.2%'",
      "fast_text": "e.g. 'Neo banking fastest-growing'",
      "fast_cagr": "e.g. 'CAGR 18.7%'"
    }}] or null,
    "drivers": [{{
      "driver": "string",
      "impact": "e.g. '+2.5%'",
      "relevance": "string",
      "timeline": "e.g. 'Medium term (2-4 years)'",
      "term": "short | medium | long"
    }}] or null
  }} or null,
  "competitors": [{{"category": "string", "names": ["string"]}}] or null
}}

Use at most 8 process_steps, 4 market segments, 6 drivers, 4 competitor groups.

TEXT:
{text}

Return only the JSON object, no other text.
"""


def extract_facts(raw_text: str, force_mock: bool = False) -> ExtractedFacts:
    api_key = os.environ.get("GROQ_API_KEY")

    if api_key and not force_mock:
        return _extract_via_api(raw_text, api_key)
    return _mock_extract(raw_text)


def _extract_via_api(raw_text: str, api_key: str) -> ExtractedFacts:
    from groq import Groq   

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=raw_text)}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    data = json.loads(completion.choices[0].message.content)
    return ExtractedFacts.model_validate(data)


def _mock_extract(raw_text: str) -> ExtractedFacts:
    return ExtractedFacts(
        company_name="Example Co",
        one_liner="A mock extraction result for pipeline testing.",
        tagline="Fast, secure, scalable and sustainable",
        ask_amount="₹14 Cr",
        allocation=[
            {"label": "Other indirect expenses", "percent": 6.94},
            {"label": "Team", "percent": 3.02},
            {"label": "Marketing Exps", "percent": 2.57},
            {"label": "Direct expenses", "percent": 1.95},
            {"label": "Capex", "percent": 0.22},
            {"label": "Contingency / Buffer", "percent": 85.30},
        ],
        process_steps=[
            {"title": "Biometric POS checkout", "description": "Seamless workflow at the counter."},
            {"title": "Onboarding", "description": "Customer onboarded via app with eKYC and UAE Pass integration."},
            {"title": "Fingerprint tap", "description": "Random fingerprint prompt ensures anti-spoofing security."},
            {"title": "Authentication", "description": "Real-time authentication via SIM-enabled connection."},
            {"title": "Transaction", "description": "Completed within seconds."},
            {"title": "Invoice", "description": "Sent via WhatsApp/SMS by default; print copy on request."},
            {"title": "Data sync", "description": "Synced with UAE Pass, loyalty programs and analytics engines."},
            {"title": "Auto-clean", "description": "Terminal auto-cleans, ready for next customer."},
        ],
        market={
            "title": "Global FinTech Market",
            "cagr": "15.27%",
            "start": {"year": 2025, "value": "USD 320.81 Bn"},
            "end": {"year": 2030, "value": "USD 652.80 Bn"},
            "segments": [
                {"category": "Service", "leader_text": "Digital payments lead", "leader_value": "46.2%",
                 "fast_text": "Neo banking fastest-growing", "fast_cagr": "CAGR 18.7%"},
                {"category": "End-User", "leader_text": "Retail dominates", "leader_value": "62.1%",
                 "fast_text": "Business grows faster", "fast_cagr": "CAGR 16.5%"},
                {"category": "Interface", "leader_text": "Mobile apps tops", "leader_value": "57.8%",
                 "fast_text": "POS/IoT faster", "fast_cagr": "CAGR 17.9%"},
                {"category": "Region", "leader_text": "APAC largest", "leader_value": "44.86%",
                 "fast_text": "Grows at", "fast_cagr": "CAGR 16.02%"},
            ],
            "drivers": [
                {"driver": "Real-time payments mandates", "impact": "+2.5%",
                 "relevance": "North America, Europe, Asia-Pacific", "timeline": "Medium term (2-4 years)", "term": "medium"},
                {"driver": "Open-banking & API standardization", "impact": "+2.2%",
                 "relevance": "Europe, South America, Global rollout", "timeline": "Medium term (2-4 years)", "term": "medium"},
                {"driver": "CBDC pilots in China & India", "impact": "+1.8%",
                 "relevance": "Asia-Pacific, Global spillover", "timeline": "Long term (≥4 years)", "term": "long"},
                {"driver": "Rise of embedded finance on Asian e-commerce platforms", "impact": "+2%",
                 "relevance": "Asia-Pacific, North America", "timeline": "Short term (≤2 years)", "term": "short"},
                {"driver": "SME credit gap in MENA & South America", "impact": "+1.5%",
                 "relevance": "Middle East, North Africa, South America", "timeline": "Medium term (2-4 years)", "term": "medium"},
                {"driver": "ESG-linked fintech solutions", "impact": "+1.2%",
                 "relevance": "Europe, North America, Asia-Pacific", "timeline": "Long term (≥4 years)", "term": "long"},
            ],
        },
        competitors=[
            {"category": "Mobile Wallets", "names": ["Ziina", "UPI", "PayBy", "Quantix", "Etisalat", "Careem Pay"]},
            {"category": "Credit & Debit cards", "names": ["Emirates NBD", "Mashreq", "ADCB", "Mastercard", "FAB", "Citi", "Dubai Islamic Bank", "HSBC", "Visa"]},
            {"category": "Blockchain Network", "names": ["Qashio", "Tarabut", "Polygon", "Norbloc", "Tabby", "Wazirx", "Rain", "Hubpay", "InvoiceMate", "Bybit"][:9]},
            {"category": "Biometric & Physical Payments", "names": ["PayByFace", "One", "Touch", "ADIB", "FingoPay", "Astra Tech"]},
        ],
    )