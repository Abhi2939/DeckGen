from pptx.util import Pt
from pptx.dml.color import RGBColor


PALETTE = {
    "primary": RGBColor(0x0C, 0x44, 0x7C),
    "accent": RGBColor(0x37, 0x8A, 0xDD),
    "accent_light": RGBColor(0xB5, 0xD4, 0xF4),
    "neutral_dark": RGBColor(0x2C, 0x2C, 0x2A),
    "neutral_light": RGBColor(0xF1, 0xEF, 0xE8),
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "chart_series": ["0C447C", "378ADD", "85B7EB", "B5D4F4"],
}

FONT_NAME = "Calibri"
TITLE_SIZE = Pt(28)
BODY_SIZE = Pt(14)
LABEL_SIZE = Pt(12)

