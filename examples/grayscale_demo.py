"""
grayscale_demo.py — 4-grayscale mode demonstration for pico-paper-lib.

Displays four horizontal bands in each of the four gray levels available
on the Waveshare 2.9" e-paper (SSD1680), with labeled text in contrasting
colors.  Then shows gradient bars and a mixed-tone composition.

4-gray mode uses portrait orientation (128×296) and the GS2_HMSB
framebuffer format.  Each pixel is 2 bits:
  0x00 = black, 0x01 = dark gray, 0x02 = light gray, 0x03 = white

Upload & run:
  pico_ctl upload examples/grayscale_demo.py /grayscale_demo.py
  pico_ctl run grayscale_demo.py
"""

from pico_paper_lib.display import (
    Display4Gray,
    GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE,
)
import time
import gc

# --- Initialise 4-gray display (portrait 128×296) ---
g = Display4Gray()

# =================================================================
# PAGE 1 — Four Gray Bands
# Shows each of the 4 gray levels as a horizontal band across the
# full 128-pixel width, with contrasting text labels.
# =================================================================
g.clear()

band_h = 74  # 296 / 4 = 74 pixels per band

# Band 1: Black background, white text
g.fill_rect(0, 0, 128, band_h, GRAY_BLACK)
g.text('BLACK', 10, 33, GRAY_WHITE)
g.text('(0x00)', 10, 45, GRAY_WHITE)

# Band 2: Dark gray background, light gray text
g.fill_rect(0, band_h, 128, band_h, GRAY_DARKGRAY)
g.text('DARK GRAY', 10, band_h + 33, GRAY_LIGHTGRAY)
g.text('(0x01)', 10, band_h + 45, GRAY_LIGHTGRAY)

# Band 3: Light gray background, dark gray text
g.fill_rect(0, band_h * 2, 128, band_h, GRAY_LIGHTGRAY)
g.text('LIGHT GRAY', 10, band_h * 2 + 33, GRAY_DARKGRAY)
g.text('(0x02)', 10, band_h * 2 + 45, GRAY_DARKGRAY)

# Band 4: White background, black text
g.fill_rect(0, band_h * 3, 128, band_h, GRAY_WHITE)
g.text('WHITE', 10, band_h * 3 + 33, GRAY_BLACK)
g.text('(0x03)', 10, band_h * 3 + 45, GRAY_BLACK)

print('Refreshing 4-gray page 1...')
g.refresh()
gc.collect()
print('Free mem:', gc.mem_free())
time.sleep(10)

# =================================================================
# PAGE 2 — Gradient Bars & Patterns
# Shows gradient transitions and geometric patterns using all 4 levels.
# =================================================================
g.clear()

# Title
g.text('4-GRAY PATTERNS', 8, 4, GRAY_BLACK)

# Gradient bar: 4 columns showing each gray level side by side
bar_w = 32  # 128 / 4
bar_y = 20
bar_h = 40
colors = [GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE]
labels = ['BLK', 'DRK', 'LGT', 'WHT']
for i, c in enumerate(colors):
    g.fill_rect(i * bar_w, bar_y, bar_w, bar_h, c)
    # Label in contrasting color
    lbl_c = GRAY_WHITE if c <= GRAY_DARKGRAY else GRAY_BLACK
    g.text(labels[i], i * bar_w + 4, bar_y + 16, lbl_c)

# Checkerboard pattern (16×16 squares, 4 gray levels)
check_y = 70
g.text('Checkerboard:', 8, check_y, GRAY_BLACK)
check_y += 12
sq = 16
for row in range(4):
    for col in range(8):
        c = colors[(row + col) % 4]
        g.fill_rect(col * sq, check_y + row * sq, sq, sq, c)

# Concentric rectangles in different gray levels
conc_y = check_y + 70
g.text('Concentric:', 8, conc_y, GRAY_BLACK)
conc_y += 12
g.fill_rect(10, conc_y, 108, 60, GRAY_BLACK)
g.fill_rect(20, conc_y + 10, 88, 40, GRAY_DARKGRAY)
g.fill_rect(30, conc_y + 18, 68, 24, GRAY_LIGHTGRAY)
g.fill_rect(40, conc_y + 24, 48, 12, GRAY_WHITE)

# Horizontal lines in each gray level
lines_y = conc_y + 70
g.text('Gray lines:', 8, lines_y, GRAY_BLACK)
lines_y += 12
for i in range(4):
    g.hline(10, lines_y + i * 8, 108, colors[i])
    g.text(str(i), 0, lines_y + i * 8, GRAY_BLACK)

print('Refreshing 4-gray page 2...')
g.refresh()
gc.collect()
print('Free mem:', gc.mem_free())
time.sleep(10)

# =================================================================
# Done — sleep
# =================================================================
g.sleep()
print('4-gray demo complete.')
