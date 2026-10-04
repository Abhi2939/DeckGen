import math
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

from style import PALETTE
from renderers.common import new_slide, add_text, add_box, add_line

CX, CY, D = 5.5, 3.25, 3.1
RING_R = D / 2 * 0.94           
LEFT_X, LEFT_W = 2.5, 1.3       
RIGHT_X, RIGHT_W = 7.15, 2.4    
LABEL_H, MIN_GAP = 0.6, 0.66


def _fmt(v):
    return f"{int(v)}%" if float(v).is_integer() else f"{v:.2f}%"


def _slice_colors(items):
    """Largest slice = navy, the rest take the series colours by rank."""
    seq = ["1B365D"] + PALETTE["alloc_series"]
    order = sorted(range(len(items)), key=lambda i: -items[i].percent)
    colors = [None] * len(items)
    for rank, idx in enumerate(order):
        colors[idx] = seq[rank % len(seq)]
    return colors


def _spread(tops, lo, hi, gap):
    """Push label tops apart so they never overlap, keeping them inside [lo, hi]."""
    tops = [min(max(t, lo), hi) for t in tops]
    for i in range(1, len(tops)):
        tops[i] = max(tops[i], tops[i - 1] + gap)
    if tops and tops[-1] > hi:
        tops[-1] = hi
        for i in range(len(tops) - 2, -1, -1):
            tops[i] = min(tops[i], tops[i + 1] - gap)
    return tops


def render(prs, facts):
    slide = new_slide(prs, "white")
    items = facts.allocation
    colors = _slice_colors(items)

    add_text(slide, 0.5, 0.3, 8, 0.6, "Ask and Allocation", 28, True, "navy")


    add_box(slide, 0, 1.55, 2.35, 2.7, "navy")
    if facts.ask_amount:
        add_text(slide, 0.1, 2.15, 2.15, 0.3, "TOTAL ASK", 11, True, "accent_light", PP_ALIGN.CENTER)
        add_text(slide, 0.1, 2.5, 2.15, 0.9, facts.ask_amount, 34, True, "white", PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)

   
    cd = CategoryChartData()
    cd.categories = [i.label for i in items]
    cd.add_series("Allocation", [i.percent for i in items])
    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT, Inches(CX - D / 2), Inches(CY - D / 2), Inches(D), Inches(D), cd
    ).chart
    chart.has_title = False
    chart.has_legend = False
    chart.plots[0].has_data_labels = False
    for i, pt in enumerate(chart.plots[0].series[0].points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = RGBColor.from_string(colors[i])
        pt.format.line.color.rgb = PALETTE["white"]
        pt.format.line.width = Pt(1.5)
    hole = chart._chartSpace.xpath(".//c:holeSize")
    if hole:
        hole[0].set("val", "68")

    add_text(slide, CX - 0.65, CY - 0.3, 1.3, 0.6, "Fund\nAllocation", 13, True, "navy",
             PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)

   
    total = sum(i.percent for i in items) or 1
    acc, placed = 0.0, []
    for idx, it in enumerate(items):
        span = it.percent / total * 360
        theta = math.radians(acc + span / 2)
        acc += span
        ex, ey = CX + RING_R * math.sin(theta), CY - RING_R * math.cos(theta)
        placed.append({"idx": idx, "right": math.sin(theta) >= 0, "ex": ex, "ey": ey,
                       "want": CY - (RING_R + 0.3) * math.cos(theta) - LABEL_H / 2})

    for side in (True, False):
        group = sorted([p for p in placed if p["right"] == side], key=lambda p: p["want"])
        tops = _spread([p["want"] for p in group], 1.2, 5.55 - LABEL_H, MIN_GAP)
        for p, top in zip(group, tops):
            it = items[p["idx"]]
            if side:
                x, w, align, ax = RIGHT_X, RIGHT_W, PP_ALIGN.LEFT, RIGHT_X - 0.08
            else:
                x, w, align, ax = LEFT_X, LEFT_W, PP_ALIGN.RIGHT, LEFT_X + LEFT_W + 0.08
            add_line(slide, p["ex"], p["ey"], ax, top + 0.17, "gray_text", 0.75, dashed=True)
            add_text(slide, x, top, w, 0.34, _fmt(it.percent), 18, True, "navy", align)
            add_text(slide, x, top + 0.32, w, 0.3, it.label, 10.5, False, "neutral_dark", align)

    return slide