from schemas import ExtractedFacts, DeckPlan


def plan_deck(facts: ExtractedFacts) -> DeckPlan:
    slide_types = []

    if facts.allocation:
        slide_types.append("fund_allocation")
    if facts.market and (facts.market.segments or facts.market.drivers or facts.market.end):
        slide_types.append("market_overview")
    if facts.process_steps:
        slide_types.append("how_it_works")
    if facts.competitors:
        slide_types.append("competitive_landscape")

    return DeckPlan(slide_types=slide_types)