import argparse 
from pptx import Presentation
from pptx.util import Inches

from extraction import extract_facts
from planner import plan_deck
from renderers import fund_allocation,how_it_works

RENDERERS = {
    "fund_allocation": fund_allocation,
    "how_it_works": how_it_works
}

def generate_deck(raw_text: str, output_path: str) -> None:

    facts = extract_facts(raw_text)
    print(f"[extraction] {facts.model_dump_json(indent=2)}\n")

    plan = plan_deck(facts)
    print(f"[planner] slides to build: {plan.slide_types}\n")

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)

    for slide_type in plan.slide_types:

        renderers = RENDERERS.get(slide_type)
        if renderers is None:
            print(f"[warn] no renderer registered for '{slide_type}', skipping")
            continue

        renderers(prs,facts)

        print(f"[render] built '{slide_type}' slide")

    prs.save(output_path)
    print(f"\nSaved: {output_path}")

