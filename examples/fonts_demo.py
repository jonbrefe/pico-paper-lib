"""
fonts_demo.py — Showcase the two built-in bitmap fonts and text alignment.

Demonstrates:
  - Font5x7 (font_small): compact 5×7-pixel glyphs, 1 px gap → 6 px per char
  - Font8x8 (font_medium): medium 8×8-pixel glyphs, 1 px gap → 9 px per char
  - Full ASCII character sets rendered in each font
  - Three text alignments: left, centred, and right
  - text_in_rect() with word-wrap and centred alignment inside a box

The display is 296×128 pixels in landscape orientation.

Upload & run:
  pico_ctl upload examples/fonts_demo.py /fonts_demo.py
  pico_ctl run fonts_demo.py
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK
from pico_paper_lib.fonts import font_small, font_medium

# --- Initialise ---
d = Display()
d.clear()

W = d.width   # 296 px (landscape)
mid = W // 2  # 148 — horizontal centre of the display

# ---- Header ----
# Use the 8×8 font for the title, then draw a solid divider below it.
d.set_font(font_medium)
d.text('Font Demo', 4, 2)
d.divider(13)  # full-width solid line at y=13

# ---- Font5x7 section ----
# Switch to the small font and print the full printable ASCII range.
# Each glyph is 5 px wide + 1 px gap = 6 px cell.
# 296 / 6 ≈ 49 characters fit on one line.
d.set_font(font_small)
d.text('Font5x7 (5x7 px)', 4, 18)       # section label
d.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 4, 28)   # uppercase
d.text('abcdefghijklmnopqrstuvwxyz', 4, 37)   # lowercase
d.text('0123456789 !@#$%^&*()', 4, 46)        # digits & symbols

# Separator between font sections.
d.dashed_line(0, 55, W - 1, 55)

# ---- Font8x8 section ----
# Each glyph is 8 px wide + 1 px gap = 9 px cell.
# 296 / 9 ≈ 32 characters fit on one line.
d.set_font(font_medium)
d.text('Font8x8 (8x8 px)', 4, 59)      # section label
d.text('ABCDEFGHIJKLMNOPQ', 4, 70)      # uppercase (partial, fits width)
d.text('abcdefghijklmnopq', 4, 81)      # lowercase (partial)

d.dashed_line(0, 92, W - 1, 92)

# ---- Alignment demo ----
# Show left, centred, and right text on the same row.
d.set_font(font_small)
d.text('<- Left', 0, 96)                       # left-aligned at x=0
d.text_centered('Center', mid, 96)              # centred around x=148
d.text_right('Right ->', W, 96)                 # right edge at x=296

# ---- text_in_rect with word-wrap ----
# Left box: text wraps automatically when wrap=True and the string exceeds
# the box width.  Alignment defaults to left/top.
d.rect(4, 105, 140, 22)               # draw the bounding box
d.text_in_rect('Wrapped text inside a bounding box for demo',
               4, 105, 140, 22, align='left', wrap=True)

# Right box: centred both horizontally and vertically inside the rect.
d.rect(150, 105, 140, 22)
d.text_in_rect('CENTER ALIGN',
               150, 105, 140, 22, align='center', valign='middle')

# ---- Refresh ----
d.refresh()
print('Fonts demo rendered.')
