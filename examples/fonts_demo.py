"""
fonts_demo.py — Show both built-in fonts and alignment options.
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK
from pico_paper_lib.fonts import font_small, font_medium

d = Display()
d.clear()

W = d.width   # 296
mid = W // 2  # 148

# Header
d.set_font(font_medium)
d.text('Font Demo', 4, 2)
d.divider(13)

# --- Font5x7 ---
d.set_font(font_small)
d.text('Font5x7 (5x7 px)', 4, 18)
d.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 4, 28)
d.text('abcdefghijklmnopqrstuvwxyz', 4, 37)
d.text('0123456789 !@#$%^&*()', 4, 46)

d.dashed_line(0, 55, W - 1, 55)

# --- Font8x8 ---
d.set_font(font_medium)
d.text('Font8x8 (8x8 px)', 4, 59)
d.text('ABCDEFGHIJKLMNOPQ', 4, 70)
d.text('abcdefghijklmnopq', 4, 81)

d.dashed_line(0, 92, W - 1, 92)

# --- Alignment demo ---
d.set_font(font_small)
d.text('<- Left', 0, 96)
d.text_centered('Center', mid, 96)
d.text_right('Right ->', W, 96)

# Text in rect with wrap
d.rect(4, 105, 140, 22)
d.text_in_rect('Wrapped text inside a bounding box for demo',
               4, 105, 140, 22, align='left', wrap=True)

d.rect(150, 105, 140, 22)
d.text_in_rect('CENTER ALIGN',
               150, 105, 140, 22, align='center', valign='middle')

d.refresh()
print('Fonts demo rendered.')
