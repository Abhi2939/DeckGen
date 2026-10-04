import math
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from style import PALETTE, FONT_NAME
from renderers.common import (new_slide, add_text, add_runs, add_box, add_line,
                              add_title, add_brand_ring)

CIRCLE_D = 0.72


def render(prs, facts):
    steps = facts.process_steps[:8]
    n = len(steps)
    slide = new_slide(prs, "bg_light")

    add_title(slide, "How it works?", size=26)
    add_brand_ring(slide)
    sub = facts.tagline or facts.one_liner
    if sub:
        add_text(slide, 0.45, 0.85, 8.4, 0.4, sub, 17, True, "blue_royal")

    left, usable = 0.45, 9.1
    spacing = usable / n
    centers = []
    for i in range(n):
        cx = left + spacing * (i + 0.5)
        arc = math.sin(math.pi * i / (n - 1)) if n > 1 else 0
        centers.append((cx, 2.45 - 0.4 * arc))      

    
    for (x1, y1), (x2, y2) in zip(centers, centers[1:]):
        add_line(slide, x1, y1, x2, y2, "green", 2.25)

    card_w = min(2.2, spacing * 1.8)
    for i, (step, (cx, cy)) in enumerate(zip(steps, centers)):
        low = i % 2 == 1                               
        card_top = 4.0 if low else 3.05
        card_h = 1.2 if low else 0.85
        card_x = min(max(cx - card_w / 2, 0.25), 9.75 - card_w)

        add_line(slide, cx, cy + CIRCLE_D / 2, cx, card_top, "gray_text", 0.75, dashed=True)
        add_box(slide, card_x, card_top, card_w, card_h, "white", MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        add_text(slide, card_x + 0.1, card_top + 0.1, card_w - 0.2, 0.3, step.title, 10.5, True, "neutral_dark")
        add_text(slide, card_x + 0.1, card_top + 0.4, card_w - 0.2, card_h - 0.45, step.description, 9, False, "gray_text")

        circ = add_box(slide, cx - CIRCLE_D / 2, cy - CIRCLE_D / 2, CIRCLE_D, CIRCLE_D, "green", MSO_SHAPE.OVAL)
        add_text(slide, cx - CIRCLE_D / 2, cy - CIRCLE_D / 2, CIRCLE_D, CIRCLE_D, str(i + 1), 20, True, "white",
                 PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    return slide