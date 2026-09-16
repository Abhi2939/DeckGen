# DeckGen

DeckGen is a Python-based pitch-deck generator. It turns a plain-language company description into a PowerPoint presentation by extracting structured facts, selecting the relevant slide types, and rendering each slide with `python-pptx`.

## Current capabilities

- Extract company name, one-liner, funding ask, allocation data, and process steps from a description.
- Use Groq for structured JSON extraction when `GROQ_API_KEY` is configured.
- Fall back to mock data when no API key is available, making the rendering pipeline easy to test locally.
- Generate a 16:9 PowerPoint deck with a shared visual system.
- Render these slide types:
  - **Ask and allocation**: funding ask plus a doughnut allocation chart.
  - **How it works**: numbered horizontal process-flow diagram.

## Architecture

```text
Company description
        |
        v
extraction.py  ->  ExtractedFacts
        |
        v
planner.py     ->  DeckPlan
        |
        v
renderers/     ->  PowerPoint slides
        |
        v
output.pptx
```

| File | Purpose |
| --- | --- |
| `main.py` | Command-line entry point and deck-generation orchestration. |
| `extraction.py` | Groq-based fact extraction and mock fallback data. |
| `schemas.py` | Pydantic models shared by each pipeline stage. |
| `planner.py` | Selects slides based on the facts that are available. |
| `style.py` | Shared palette, font, and type sizes. |
| `renderers/fund_allocation.py` | Renders the funding/allocation slide. |
| `renderers/how_it_works.py` | Renders the process-flow slide. |

## Requirements

- Python 3.10 or later
- A Groq API key for live AI extraction (optional)

Install dependencies:

```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

`.env` is already ignored by Git. Do not commit API keys.

If `GROQ_API_KEY` is missing, DeckGen uses built-in mock data instead of making an API request.

## Usage

Generate a deck from a description:

```powershell
python main.py --description "Acme Pay is raising Rs. 14 Cr. We will allocate 60% to buffer, 20% to team, 12% to marketing, 5% to direct expenses, and 3% to capex. Customers sign up, complete verification, transact, and sync analytics data." --output acme_pitch_deck.pptx
```

Or generate a deck from a text file:

```powershell
python main.py --file company_description.txt --output pitch_deck.pptx
```

The default output filename is `output.pptx`.

## Extraction schema

The extraction step validates data against this structure:

```python
ExtractedFacts(
    company_name: str,
    one_liner: str | None,
    ask_amount: str | None,
    allocation: list[AllocationItem] | None,
    process_steps: list[ProcessStep] | None,
)
```

The planner only renders slides with corresponding usable data. For example, no allocation chart is created if the source description does not contain allocation information.

## Extending DeckGen

To add a slide type:

1. Add the required fields to `ExtractedFacts` in `schemas.py`.
2. Update the extraction prompt in `extraction.py`.
3. Add the slide-selection condition in `planner.py`.
4. Create a renderer in `renderers/`.
5. Register the renderer in `RENDERERS` in `main.py`.

## Notes

- Slide layout and colors are deterministic; only fact extraction is AI-assisted.
- The current visual theme is defined centrally in `style.py`.
- Groq is called with JSON-object response formatting and a temperature of `0` to keep extraction predictable.
