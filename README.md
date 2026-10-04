# DeckGen

DeckGen is a Python-based pitch-deck generator. It turns a plain-language company description into a PowerPoint presentation by extracting structured facts, selecting the relevant slide types, and rendering each slide with `python-pptx`. It can be run from the command line or through a Streamlit web app.

## Current capabilities

- Extract company name, one-liner, tagline, funding ask, allocation data, process steps, market data, and competitors from a description.
- Use Groq for structured JSON extraction when `GROQ_API_KEY` is configured.
- Fall back to mock data when no API key is available (or when `--mock` is passed), making the rendering pipeline easy to test locally.
- Generate a 16:9 PowerPoint deck with a shared visual system modelled on the reference decks.
- Render these slide types:
  - **Ask and allocation**: navy ask panel, doughnut allocation chart, and percentage callouts connected to each slice.
  - **Market overview**: 2025 vs 2030 market-size cards, four segment stat columns with CAGR, and a drivers table with colour-coded impact timelines.
  - **How it works**: up to 8 numbered steps on an arc, with alternating description cards.
  - **Competitive landscape**: 2x2 grid of competitor categories with names (or logos, if provided).
- Skip any slide that has no usable data in the description.
- Run as a Streamlit app: paste a description, generate the deck, and download the `.pptx`.

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
| `app.py` | Streamlit web app wrapping `generate_deck`. |
| `extraction.py` | Groq-based fact extraction and mock fallback data. |
| `schemas.py` | Pydantic models shared by each pipeline stage. |
| `planner.py` | Selects slides based on the facts that are available. |
| `style.py` | Shared palette, font, and type sizes. |
| `renderers/common.py` | Shared drawing helpers (text, boxes, dotted lines, title, brand ring). |
| `renderers/fund_allocation.py` | Renders the ask and allocation slide. |
| `renderers/market_overview.py` | Renders the market size, segment stats, and drivers table. |
| `renderers/how_it_works.py` | Renders the numbered process flow. |
| `renderers/competitive_landscape.py` | Renders the 2x2 competitor grid. |
| `assets/logos/` | Optional competitor logos (see below). |

## Requirements

- Python 3.10 or later
- A Groq API key for live AI extraction (optional)

`requirements.txt`:

```text
streamlit
python-pptx
pydantic
groq
python-dotenv
```

Install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

`.env` is ignored by Git. Do not commit API keys.

If `GROQ_API_KEY` is missing, DeckGen uses built-in mock data instead of making an API request. The mock ignores the input text, so a deck titled "Example Co" means the key was not picked up.

## Usage

### Command line

Generate a deck from a description:

```powershell
python main.py --description "Acme Pay is raising Rs. 14 Cr. We will allocate 60% to buffer, 20% to team, 12% to marketing, 5% to direct expenses, and 3% to capex. Customers sign up, complete verification, transact, and sync analytics data." --output acme_pitch_deck.pptx
```

Or generate a deck from a text file (read as UTF-8, so `₹` is preserved on Windows):

```powershell
python main.py --file company_description.txt --output pitch_deck.pptx
```

Test the renderers without calling the API:

```powershell
python main.py --mock --output preview.pptx
```

| Flag | Meaning |
| --- | --- |
| `--description` | Company description as text. |
| `--file` | Path to a text file containing the description. |
| `--output` | Output filename (default `output.pptx`). |
| `--mock` | Skip Groq and use the built-in mock data. |

### Streamlit app

```powershell
streamlit run app.py
```

Paste a company description, click **Generate deck**, then download the `.pptx`.

## What the description needs to contain

The extractor is instructed not to invent numbers, names, or percentages, so each slide appears only if the description contains its facts:

| Slide | Description must include |
| --- | --- |
| Ask and allocation | A funding amount and an allocation breakdown (percentages per use). |
| Market overview | Market size (start/end values and years) and/or segment stats and/or growth drivers. Include CAGR figures if you want them shown. |
| How it works | A sequence of steps or a process description. |
| Competitive landscape | Competitor names grouped by category. |

## Extraction schema

The extraction step validates data against this structure:

```python
ExtractedFacts(
    company_name: str,
    one_liner: str | None,
    tagline: str | None,                       # subtitle on "How it works"
    ask_amount: str | None,
    allocation: list[AllocationItem] | None,   # label, percent
    process_steps: list[ProcessStep] | None,   # title, description
    market: MarketData | None,
    competitors: list[CompetitorGroup] | None, # category, names
)

MarketData(
    title: str,
    cagr: str | None,
    start: MarketValue | None,                 # year, value
    end: MarketValue | None,
    segments: list[MarketSegment] | None,      # category, leader_text, leader_value, fast_text, fast_cagr
    drivers: list[MarketDriver] | None,        # driver, impact, relevance, timeline, term (short|medium|long)
)
```

The planner only renders slides with corresponding usable data. For example, no allocation chart is created if the source description does not contain allocation information. Slides are ordered: ask and allocation, market overview, how it works, competitive landscape.

Layout limits: 8 process steps, 4 market segments, 6 drivers, 4 competitor groups, 9 names per group.

## Competitor logos (optional)

Competitor names are drawn as text chips by default. To show a logo instead, add a PNG to `assets/logos/` named after the competitor in lowercase with letters and digits only:

```text
assets/logos/visa.png
assets/logos/emiratesnbd.png
assets/logos/careempay.png
```

Logos are scaled to fit their grid cell.

## Extending DeckGen

To add a slide type:

1. Add the required fields to `ExtractedFacts` in `schemas.py`.
2. Update the extraction prompt in `extraction.py`.
3. Add the slide-selection condition in `planner.py`.
4. Create a renderer in `renderers/` (reuse the helpers in `renderers/common.py`).
5. Register the renderer in `RENDERERS` in `main.py`.

## Deployment (Streamlit Community Cloud)

1. Push the repo to GitHub. `.gitignore` should contain:

```text
   venv/
   .env
   __pycache__/
   *.pyc
   tempCodeRunnerFile.py
   *.pptx
   .vscode/
```

2. At share.streamlit.io, click **Create app**, select the repo, and set the main file to `app.py`.
3. Under **Advanced settings**, choose Python 3.11 and add the key under **Secrets**:

```toml
   GROQ_API_KEY = "your_groq_api_key"
```

Top-level secrets are exposed as environment variables, so `extraction.py` reads the key without code changes. Use relative paths only, since the app runs on Linux servers.

## Notes

- Slide layout and colors are deterministic; only fact extraction is AI-assisted.
- The visual theme is defined centrally in `style.py`; the reference-deck colours are `navy`, `green`, and `blue_royal`.
- Groq is called with JSON-object response formatting and a temperature of `0` to keep extraction predictable.
- Fonts are referenced by name (Calibri) and resolved by PowerPoint when the deck is opened.

## Known limitations

- Input is a text description only; web-link input is not supported yet.
- No business-model slide yet.
- "How it works" shows step numbers rather than icons, and the allocation slide has no decorative imagery.
- A very short description produces only the slides it has facts for.