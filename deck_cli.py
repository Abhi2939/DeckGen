"""DeckGen-style CLI: turn a plain-language description into a pitch deck.

    pip install python-pptx
    python deck_cli.py --description "FinFlow is raising Rs. 10 Cr. Process: user signs up, verifies KYC, gets funded."
    python deck_cli.py --file company_description.txt --output pitch.pptx

Extraction here is regex-based (no API key needed). Slides are only rendered
when usable data exists, like planner.py.
"""
import argparse
import re
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# ---- Style (mirrors style.py) ----
BG, CARD = RGBColor(0x0F, 0x17, 0x2A), RGBColor(0x1E, 0x29, 0x3B)
TXT, MUTED, ACC = RGBColor(0xF8, 0xFA, 0xFC), RGBColor(0x94, 0xA3, 0xB8), RGBColor(0x2D, 0xD4, 0xBF)
LINE = RGBColor(0x33, 0x41, 0x55)
PALETTE = [RGBColor(*c) for c in [(0x2D, 0xD4, 0xBF), (0x38, 0xBD, 0xF8), (0x81, 0x8C, 0xF8),
                                  (0xF4, 0x72, 0xB6), (0xFB, 0xBF, 0x24)]]
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)


def text(slide, x, y, w, h, s, size=14, bold=False, color=TXT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = s
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), bold, color
    return tb


def shape(slide, kind, x, y, w, h, fill):
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def base_slide(title, subtitle):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    text(s, 0.6, 0.4, 8.8, 0.6, title, 28, True)
    shape(s, MSO_SHAPE.RECTANGLE, 0.6, 1.05, 0.8, 0.05, ACC)
    text(s, 0.6, 1.2, 8.8, 0.35, subtitle, 14, color=MUTED)
    return s


MONEY = re.compile(r"((?:₹|Rs\.?|INR|\$|USD)\s?[\d.,]+\s?(?:Cr|crore|crores|L|lakh|lakhs|M|million|B|billion|K)?)", re.I)


def extract(desc: str) -> dict:
    desc = " ".join(desc.split())
    m = re.match(r"\s*([A-Z][\w&.\- ]*?)\s+(?:is|are|has|will)\b", desc)
    company = m.group(1).strip() if m else "Your Company"
    ask = None
    m = re.search(r"rais\w+\s+" + MONEY.pattern, desc, re.I) or MONEY.search(desc)
    if m:
        ask = m.group(1).strip().rstrip(".,")
        ask = re.sub(r"^(Rs\.?|INR)\s?", "₹", ask, flags=re.I)
        ask = re.sub(r"\s*(crores?)$", " Cr", ask, flags=re.I)
    alloc = []
    for pct, name in re.findall(r"(\d+(?:\.\d+)?)\s?%\s+(?:to|for|on|in|towards)?\s*([A-Za-z][A-Za-z ]*?)(?=\s*(?:,|;|\.|\band\b\s+\d|$))", desc):
        alloc.append((name.strip().capitalize(), float(pct)))
    steps = []
    m = re.search(r"(?:process|flow|steps?|how it works)\s*[:\-]\s*(.+)", desc, re.I)
    chunk = m.group(1) if m else None
    if not chunk:  # fall back to the last sentence with 3+ comma-separated actions
        for sent in reversed(re.split(r"(?<=[.!?])\s+", desc)):
            if sent.count(",") >= 2 and "%" not in sent:
                chunk = sent
                break
    if chunk:
        parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", chunk.strip().rstrip("."))
        for p in filter(None, (x.strip() for x in parts)):
            words = re.sub(r"^(?:then\s+)?(?:the\s+)?(?:users?|customers?|clients?|we)\s+", "", p, flags=re.I).split()
            if not words:
                continue
            verb = words[0]
            if verb.endswith("ies") and len(verb) > 4:
                verb = verb[:-3] + "y"
            elif verb.endswith("s") and not verb.endswith("ss"):
                verb = verb[:-1]
            head = " ".join([verb] + words[1:3])
            head = head[0].upper() + head[1:]
            steps.append((head, p[0].upper() + p[1:]))
    return {"company": company, "ask": ask, "allocation": alloc or None, "steps": steps[:6] or None}


def ask_slide(f):
    s = base_slide("The Ask", f"{f['company']} — funding requirement and use of funds")
    card = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.6, 1.9, 3.4, 3.0, CARD)
    card.adjustments[0] = 0.05
    text(s, 0.6, 2.2, 3.4, 0.3, "RAISING", 12, True, MUTED, PP_ALIGN.CENTER)
    text(s, 0.6, 2.6, 3.4, 1.0, f["ask"] or "—", 54, True, ACC, PP_ALIGN.CENTER)
    top = max(f["allocation"], key=lambda a: a[1])
    text(s, 0.6, 3.8, 3.4, 0.4, f"Largest share: {top[0]} ({top[1]:g}%)", 14, align=PP_ALIGN.CENTER)
    cd = CategoryChartData()
    cd.categories = [n for n, _ in f["allocation"]]
    cd.add_series("Allocation", [v for _, v in f["allocation"]])
    chart = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(4.3), Inches(1.7), Inches(2.9), Inches(3.4), cd).chart
    chart.has_legend = chart.has_title = False
    plot = chart.plots[0]
    plot.has_data_labels = False
    for i in range(len(f["allocation"])):
        pt = plot.series[0].points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = PALETTE[i % len(PALETTE)]
        pt.format.line.color.rgb, pt.format.line.width = BG, Pt(2)
    hole = chart._chartSpace.xpath(".//c:holeSize")
    if hole:
        hole[0].set("val", "62")
    for i, (name, val) in enumerate(f["allocation"][:7]):
        y = 1.9 + i * 0.5
        col = PALETTE[i % len(PALETTE)]
        shape(s, MSO_SHAPE.OVAL, 7.35, y + 0.08, 0.18, 0.18, col)
        text(s, 7.65, y, 1.3, 0.34, name, 13, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 8.8, y, 0.7, 0.34, f"{val:g}%", 13, True, col, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)


def how_slide(f):
    steps = f["steps"]
    s = base_slide("How It Works", f"{f['company']} — from sign-up to outcome in {len(steps)} steps")
    n, gap, x0, cy = len(steps), 0.35, 0.6, 2.0
    cw = (8.8 - (n - 1) * gap) / n
    ln = s.shapes.add_connector(1, Inches(x0 + cw / 2), Inches(cy + 0.4), Inches(x0 + cw / 2 + (n - 1) * (cw + gap)), Inches(cy + 0.4))
    ln.line.color.rgb, ln.line.width = LINE, Pt(2)
    for i, (head, desc) in enumerate(steps):
        x = x0 + i * (cw + gap)
        c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, cy + 1.0, cw, 1.9, CARD)
        c.adjustments[0] = 0.06
        circ = shape(s, MSO_SHAPE.OVAL, x + cw / 2 - 0.4, cy, 0.8, 0.8, ACC)
        circ.line.color.rgb, circ.line.width = BG, Pt(3)
        text(s, x + cw / 2 - 0.4, cy, 0.8, 0.8, str(i + 1), 24, True, BG, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        text(s, x + 0.1, cy + 1.25, cw - 0.2, 0.4, head, 16 if n <= 4 else 13, True, align=PP_ALIGN.CENTER)
        text(s, x + 0.15, cy + 1.7, cw - 0.3, 0.9, desc, 12 if n <= 4 else 10, color=MUTED, align=PP_ALIGN.CENTER)


def plan(f):
    slides = []
    if f["allocation"] and f["ask"]:
        slides.append(ask_slide)
    if f["steps"]:
        slides.append(how_slide)
    return slides


def main():
    ap = argparse.ArgumentParser(description="Generate a pitch deck from a description")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--description")
    g.add_argument("--file")
    ap.add_argument("--output", default="output.pptx")
    a = ap.parse_args()
    desc = a.description or open(a.file, encoding="utf-8").read()
    facts = extract(desc)
    print("Extracted:", facts)
    slides = plan(facts)
    if not slides:
        sys.exit("No usable data found (need an allocation breakdown and/or process steps).")
    for render in slides:
        render(facts)
    prs.save(a.output)
    print(f"Saved {a.output} ({len(slides)} slide{'s' if len(slides) != 1 else ''})")


if __name__ == "__main__":
    main()