import argparse
from pptx import Presentation
from pptx.util import Inches

from extraction import extract_facts
from planner import plan_deck
from renderers import fund_allocation, market_overview, how_it_works, competitive_landscape

RENDERERS = {
    "fund_allocation": fund_allocation.render,
    "market_overview": market_overview.render,
    "how_it_works": how_it_works.render,
    "competitive_landscape": competitive_landscape.render,
}


def generate_deck(raw_text: str, output_path: str, force_mock: bool = False) -> None:
    facts = extract_facts(raw_text, force_mock=force_mock)
    print(f"[extraction] {facts.model_dump_json(indent=2)}\n")

    plan = plan_deck(facts)
    print(f"[planner] slides to build: {plan.slide_types}\n")

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)

    for slide_type in plan.slide_types:
        renderer = RENDERERS.get(slide_type)
        if renderer is None:
            print(f"[warn] no renderer registered for '{slide_type}', skipping")
            continue
        renderer(prs, facts)
        print(f"[render] built '{slide_type}' slide")

    prs.save(output_path)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--file", type=str, default=None)
    parser.add_argument("--output", type=str, default="output.pptx")
    parser.add_argument("--mock", action="store_true", help="skip the API and use built-in mock data")
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:  
            text = f.read()
    elif args.description:
        text = args.description
    else:
        text = ""

    generate_deck(text, args.output, force_mock=args.mock)