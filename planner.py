from schemas import ExtractedFacts,DeckPlan

def plan_deck(facts: ExtractedFacts) -> DeckPlan:

    slide_types = []
    
    if facts.allocation:
        slide_types.append("fund_allocation")
    if facts.process_steps:
        slide_types.append("how_it_works")

    return DeckPlan(slide_types=slide_types)
