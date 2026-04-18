"""
hello_world.py — Basic demo of pico-epaper-lib.

Draws text in two font sizes, a few shapes, and refreshes the display.
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.fonts import font_small, font_medium

d = Display()
d.clear()

# Title in large font
d.set_font(font_medium)
d.text('pico-paper-lib', 10, 5)
d.divider(16)

# Body in small font
d.set_font(font_small)
d.text('A MicroPython library for', 10, 22)
d.text('Waveshare 2.9" e-paper', 10, 32)

# Shapes showcase
d.circle(250, 40, 20)
d.circle(250, 40, 12, fill=True)

d.rounded_rect(10, 50, 80, 30, 5)
d.text_in_rect('Rounded', 10, 50, 80, 30, align='center', valign='middle')

d.triangle(120, 78, 150, 50, 180, 78, fill=True)

d.rect(200, 50, 40, 30, fill=True)

# Progress bar
d.text('Progress:', 10, 90)
d.progress_bar(70, 88, 100, 12, percent=65)

# Dashed line
d.dashed_line(10, 110, 286, 110)

# Footer
d.text_centered('v0.1.0', 148, 118)

d.refresh()
print('Done! Check the display.')
