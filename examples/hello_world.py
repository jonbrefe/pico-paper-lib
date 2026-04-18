"""
hello_world.py — Minimal getting-started example for pico-paper-lib.

Demonstrates the most common features in a single page:
  - Creating a Display in landscape mode (296×128)
  - Drawing text with two built-in fonts (5×7 and 8×8)
  - Basic shapes: circle, rounded rectangle, triangle, filled rectangle
  - The progress_bar() widget
  - Dashed lines and full-width dividers
  - Centred text for a footer

Hardware:
  - Raspberry Pi Pico W
  - Waveshare 2.9" e-paper (SSD1680), SPI wired to default pins

Upload & run:
  pico_ctl upload examples/hello_world.py /hello_world.py
  pico_ctl run hello_world.py
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.fonts import font_small, font_medium

# --- Initialise display ---
# Display() creates a 296×128 landscape canvas and wakes the hardware.
# All drawing happens in an in-memory framebuffer until refresh() is called.
d = Display()
d.clear()  # fill the canvas with WHITE

# --- Title bar (8×8 font) ---
# set_font() changes the default font for all subsequent text() calls.
d.set_font(font_medium)
d.text('pico-paper-lib', 10, 5)
# divider() draws a full-width horizontal line; style can be 'solid',
# 'dashed', or 'dotted'.
d.divider(16)

# --- Body text (5×7 font) ---
# Switching back to the compact font for body copy.
d.set_font(font_small)
d.text('A MicroPython library for', 10, 22)
d.text('Waveshare 2.9" e-paper', 10, 32)

# --- Shapes showcase ---
# Concentric circles: outline then filled inner circle.
# circle(cx, cy, radius, color=BLACK, fill=False)
d.circle(250, 40, 20)               # outer ring
d.circle(250, 40, 12, fill=True)    # solid inner

# Rounded rectangle with centred text inside.
# rounded_rect(x, y, w, h, corner_radius, color=BLACK, fill=False)
d.rounded_rect(10, 50, 80, 30, 5)
# text_in_rect() draws text inside a bounding box with alignment & wrap.
d.text_in_rect('Rounded', 10, 50, 80, 30, align='center', valign='middle')

# Filled triangle: three vertices (x0,y0), (x1,y1), (x2,y2).
d.triangle(120, 78, 150, 50, 180, 78, fill=True)

# Simple filled rectangle.
# rect(x, y, w, h, color=BLACK, fill=False)
d.rect(200, 50, 40, 30, fill=True)

# --- Progress bar widget ---
# progress_bar(x, y, w, h, percent, color=BLACK)
# Draws an outlined bar filled proportionally to `percent` (0–100).
d.text('Progress:', 10, 90)
d.progress_bar(70, 88, 100, 12, percent=65)

# --- Dashed line ---
# dashed_line(x0, y0, x1, y1, color=BLACK, dash=4, gap=3)
d.dashed_line(10, 110, 286, 110)

# --- Footer ---
# text_centered(s, cx, y) centres the string horizontally around cx.
d.text_centered('v0.1.0', 148, 118)

# --- Push to display ---
# refresh() transfers the framebuffer to the e-paper via SPI and triggers
# a full-screen hardware update (~2 s black/white flash).
d.refresh()
print('Done! Check the display.')
