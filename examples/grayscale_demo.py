"""
grayscale_demo.py — 4-grayscale mode demonstration for pico-paper-lib.

Displays four horizontal bands in each of the four gray levels available
on the Waveshare 2.9" e-paper (SSD1680), with labeled text in contrasting
colors.  Then shows gradient bars and a mixed-tone composition.

4-gray mode uses landscape orientation (296×128, default) with the GS2_HMSB
framebuffer format.  Each pixel is 2 bits:
  0x00 = black, 0x01 = light gray, 0x02 = dark gray, 0x03 = white

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

# --- Initialise 4-gray display (landscape 296×128) ---
g = Display4Gray()

# =================================================================
# PAGE 1 — Four Gray Bands
# Shows each of the 4 gray levels as a vertical band across the
# full 128-pixel height, with contrasting text labels.
# =================================================================
g.clear()

band_w = 74  # 296 / 4 = 74 pixels per band

# Band 1: Black background, white text
g.fill_rect(0, 0, band_w, 128, GRAY_BLACK)
g.text('BLACK', 10, 55, GRAY_WHITE)
g.text('(0x00)', 10, 67, GRAY_WHITE)

# Band 2: Dark gray background, light gray text
g.fill_rect(band_w, 0, band_w, 128, GRAY_DARKGRAY)
g.text('DARK', band_w + 10, 55, GRAY_LIGHTGRAY)
g.text('(0x02)', band_w + 10, 67, GRAY_LIGHTGRAY)

# Band 3: Light gray background, dark gray text
g.fill_rect(band_w * 2, 0, band_w, 128, GRAY_LIGHTGRAY)
g.text('LIGHT', band_w * 2 + 10, 55, GRAY_DARKGRAY)
g.text('(0x01)', band_w * 2 + 10, 67, GRAY_DARKGRAY)

# Band 4: White background, black text
g.fill_rect(band_w * 3, 0, band_w, 128, GRAY_WHITE)
g.text('WHITE', band_w * 3 + 10, 55, GRAY_BLACK)
g.text('(0x03)', band_w * 3 + 10, 67, GRAY_BLACK)

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
bar_w = 74  # 296 / 4
bar_y = 20
bar_h = 30
colors = [GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE]
labels = ['BLK', 'DRK', 'LGT', 'WHT']
for i, c in enumerate(colors):
    g.fill_rect(i * bar_w, bar_y, bar_w, bar_h, c)
    lbl_c = GRAY_WHITE if c <= GRAY_DARKGRAY else GRAY_BLACK
    g.text(labels[i], i * bar_w + 4, bar_y + 11, lbl_c)

# Checkerboard pattern (16×16 squares, 4 gray levels)
check_y = 55
g.text('Checkerboard:', 8, check_y, GRAY_BLACK)
check_y += 12
sq = 16
for row in range(4):
    for col in range(16):
        c = colors[(row + col) % 4]
        g.fill_rect(col * sq + 8, check_y + row * sq, sq, sq, c)

# Concentric rectangles in different gray levels
conc_x = 8
conc_y = check_y - 12
g.fill_rect(conc_x, conc_y, 108, 60, GRAY_BLACK)
g.fill_rect(conc_x + 10, conc_y + 10, 88, 40, GRAY_DARKGRAY)
g.fill_rect(conc_x + 20, conc_y + 18, 68, 24, GRAY_LIGHTGRAY)
g.fill_rect(conc_x + 30, conc_y + 24, 48, 12, GRAY_WHITE)

# Horizontal lines in each gray level (right half of screen)
lines_x = 160
lines_y = 55
g.text('Gray lines:', lines_x, lines_y, GRAY_BLACK)
lines_y += 12
for i in range(4):
    g.hline(lines_x, lines_y + i * 8, 120, colors[i])
    g.text(str(i), lines_x + 125, lines_y + i * 8, GRAY_BLACK)

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
