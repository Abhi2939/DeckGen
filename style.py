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

    "navy": RGBColor(0x1B, 0x36, 0x5D),         
    "green": RGBColor(0x6F, 0xB8, 0x1E),         
    "blue_royal": RGBColor(0x2B, 0x3A, 0xA8),    
    "bg_light": RGBColor(0xF3, 0xF4, 0xF6),     
    "gray_text": RGBColor(0x6B, 0x72, 0x80),
    "border": RGBColor(0xD9, 0xDC, 0xE1),
    "row_alt": RGBColor(0xF7, 0xF7, 0xF7),
    "term_short": RGBColor(0xF8, 0xD7, 0xDA),    
    "term_medium": RGBColor(0xFF, 0xE3, 0xA3),   
    "term_long": RGBColor(0xD6, 0xE9, 0xB4),     

    "alloc_series": ["FFC000", "F26B1D", "1F5FD9", "B8B8B8", "8FA3BF", "D0D0D0", "6FB81E"],
}

FONT_NAME = "Calibri"
TITLE_SIZE = Pt(28)
BODY_SIZE = Pt(14)
LABEL_SIZE = Pt(12)

