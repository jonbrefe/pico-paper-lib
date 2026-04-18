"""
test_all.py — Comprehensive visual test suite for pico-paper-lib.

Renders 7 full-screen pages on the Waveshare 2.9" e-paper display,
exercising every public method of the Display and Display4Gray classes.
After each page the script pauses for a configurable number of seconds
so the user can photograph the display for visual review.

Pages:
  1. Lines & Pixels   — line(), hline(), vline(), dashed_line(),
                         dotted_line(), pixel(), divider(), thickness
  2. Shapes            — rect(), rounded_rect(), circle(), ellipse(),
                         triangle(), polygon(), fill variants, nesting
  3. Text Features     — Font5x7 / Font8x8 full character sets,
                         text_centered(), text_right(), set_font(),
                         extended Latin characters (ÁÉÍÓÚÑ etc.)
  4. Text Layout       — text_in_rect() (align, valign, wrap),
                         text_wrapped(), badge(), mixed-font lines
  5. Widgets           — bordered_panel(), progress_bar(), table(),
                         divider styles, icon() with raw bitmap data
  6. Edge Cases        — full-screen border, corner text, tiny shapes,
                         overlapping shapes, max text length clipping,
                         large circles/ellipses, thick diagonal lines
  7. 4-Grayscale       — Display4Gray, 4 gray bands, gradient bar,
                         checkerboard, concentric rects, gray lines

The loop repeats indefinitely (with a 10 s pause between loops) so the
test can run unattended while monitoring via serial or `pico_ctl watch`.

Upload & run:
  pico_ctl upload examples/test_all.py /test_all.py
  pico_ctl run test_all.py
"""

from pico_paper_lib import Display, Display4Gray
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.display import GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE
from pico_paper_lib.fonts import font_small, font_medium
import time
import gc

# --- Initialise display (landscape 296×128, default SPI pins) ---
d = Display()

def pause(label, seconds=8):
    """Print a page label to the serial console, run garbage collection,
    and wait `seconds` so the display can be photographed.
    
    Args:
        label:   Human-readable page name (printed to serial).
        seconds: How long to wait before moving on (default 8 s).
    """
    print('--- PAGE:', label, '--- (waiting', seconds, 's)')
    gc.collect()
    print('Free mem:', gc.mem_free())
    time.sleep(seconds)

loop = 0

while True:
    loop += 1
    print('=== LOOP', loop, '===')

    # =================================================================
    # PAGE 1 — Lines & Pixels
    # Covers: line(), hline(), vline(), dashed_line(), dotted_line(),
    #         pixel(), divider(), thickness parameter
    # =================================================================
    d.clear()

    # Inverted title bar: solid black rect with white text.
    d.fill_rect(0, 0, 296, 11, BLACK)
    # The `font=` keyword lets you use a specific font for one call
    # without changing the global default set by set_font().
    d.text('PAGE 1: Lines & Pixels', 4, 2, WHITE, font=font_medium)

    y0 = 15  # baseline for the first row

    # -- Thin line (default thickness=1) --
    d.text('thin', 2, y0)
    d.line(40, y0 + 3, 140, y0 + 3)

    # -- Thick line (thickness=3 draws parallel offset lines) --
    d.text('thick(3)', 2, y0 + 10)
    d.line(55, y0 + 13, 140, y0 + 13, thickness=3)

    # -- Dashed line (dash=4, gap=3 are the defaults) --
    d.text('dashed', 2, y0 + 22)
    d.dashed_line(45, y0 + 25, 140, y0 + 25)

    # -- Dotted line (spacing=3 default) --
    d.text('dotted', 2, y0 + 32)
    d.dotted_line(45, y0 + 35, 140, y0 + 35)

    # -- Diagonal lines: standard and thick --
    d.text('diag', 2, y0 + 44)
    d.line(40, y0 + 42, 80, y0 + 58)              # 1 px diagonal
    d.line(50, y0 + 42, 90, y0 + 58, thickness=2)  # 2 px diagonal

    # -- Horizontal and vertical convenience helpers --
    # hline(x, y, width) — faster than line() for axis-aligned.
    # vline(x, y, height)
    d.text('h/v', 2, y0 + 62)
    d.hline(30, y0 + 65, 50)   # 50 px horizontal
    d.vline(100, y0 + 55, 20)  # 20 px vertical

    # -- Individual pixels --
    d.text('pixels', 2, y0 + 76)
    for i in range(10):
        d.pixel(40 + i * 4, y0 + 79)  # 10 dots, 4 px apart

    # -- Right half: cross-hatch pattern --
    # Overlapping horizontal and vertical lines create a grid.
    d.text('cross-hatch', 150, y0)
    for i in range(0, 60, 6):
        d.line(150, y0 + 10 + i, 210, y0 + 10 + i)  # horizontal
        d.line(150 + i, y0 + 10, 150 + i, y0 + 70)  # vertical

    # -- Thick diagonal + dashed diagonal --
    d.text('thick diag', 220, y0)
    d.line(220, y0 + 12, 285, y0 + 45, thickness=2)
    d.dashed_line(220, y0 + 50, 285, y0 + 80)

    # -- Full-width dividers at the bottom --
    # divider(y, color=BLACK, style='solid') draws across the full width.
    d.divider(118, style='solid')
    d.text('solid divider ^  dashed v', 80, 109)
    d.divider(126, style='dashed')

    d.refresh()  # push framebuffer → e-paper
    pause('Lines & Pixels')

    # =================================================================
    # PAGE 2 — Shapes
    # Covers: rect(), rounded_rect(), circle(), ellipse(),
    #         triangle(), polygon(), fill=True, nesting
    # =================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 2: Shapes', 4, 2, WHITE, font=font_medium)

    # -- Row 1: Rectangles --
    # rect(x, y, w, h, color=BLACK, fill=False)
    d.text('rect', 2, 15)
    d.rect(2, 24, 30, 20)                        # outline
    d.text('fill', 36, 15)
    d.rect(36, 24, 30, 20, fill=True)             # solid fill
    # rounded_rect(x, y, w, h, corner_radius, ...)
    d.text('rounded', 72, 15)
    d.rounded_rect(72, 24, 40, 20, 5)             # r=5 outline
    d.text('rnd fill', 118, 15)
    d.rounded_rect(118, 24, 40, 20, 5, fill=True) # r=5 filled

    # -- Row 2: Circles & Ellipses --
    # circle(cx, cy, radius, color=BLACK, fill=False)
    d.text('circle', 2, 50)
    d.circle(20, 68, 10)                          # outline
    d.text('filled', 42, 50)
    d.circle(58, 68, 10, fill=True)               # filled
    # ellipse(cx, cy, rx, ry, color=BLACK, fill=False)
    d.text('ellipse', 78, 50)
    d.ellipse(108, 68, 16, 8)                     # wide outline
    d.text('ell fill', 134, 50)
    d.ellipse(160, 68, 16, 8, fill=True)          # wide filled

    # -- Row 3: Triangles & Polygons --
    # triangle(x0,y0, x1,y1, x2,y2, color=BLACK, fill=False)
    d.text('tri', 2, 84)
    d.triangle(2, 124, 22, 96, 42, 124)           # outline
    d.text('tri fill', 48, 84)
    d.triangle(48, 124, 68, 96, 88, 124, fill=True)

    # polygon(points, color=BLACK, fill=False)
    # points is a list of (x, y) tuples.
    d.text('polygon', 100, 84)
    pts = [(104, 124), (114, 96), (134, 100), (144, 118), (124, 126)]
    d.polygon(pts)                                 # outline pentagon

    d.text('poly fill', 154, 84)
    pts2 = [(158, 124), (168, 96), (188, 100), (198, 118), (178, 126)]
    d.polygon(pts2, fill=True)                     # filled pentagon

    # -- Right side: nested concentric shapes --
    # Drawing multiple circles at the same centre with decreasing radii.
    d.text('nested', 210, 15)
    d.circle(245, 50, 25)
    d.circle(245, 50, 18)
    d.circle(245, 50, 11)
    d.circle(245, 50, 4, fill=True)  # solid bullseye

    # Concentric rectangles.
    d.text('concentric', 210, 84)
    d.rect(210, 94, 50, 30)
    d.rect(215, 99, 40, 20)
    d.rect(220, 104, 30, 10)

    d.refresh()
    pause('Shapes')

    # =================================================================
    # PAGE 3 — Text Features
    # Covers: text(), set_font(), text_centered(), text_right(),
    #         Font5x7 / Font8x8, extended Latin characters
    # =================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 3: Text', 4, 2, WHITE, font=font_medium)

    # -- Font5x7: full printable ASCII --
    # Default font is font_small (5×7).  49 chars per line @ 6 px/char.
    d.text('Small 5x7:', 2, 16)
    d.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 2, 26)
    d.text('abcdefghijklmnopqrstuvwxyz', 2, 36)
    d.text('0123456789 !@#$%^&*()', 2, 46)

    # -- Font8x8: switch and render partial set --
    # 32 chars per line @ 9 px/char.
    d.set_font(font_medium)
    d.text('Medium 8x8:', 2, 58)
    d.text('ABCDEFGHIJ 0123456789', 2, 68)
    d.set_font(font_small)  # restore default

    # -- Text alignment --
    # Draw a cross-hair marker at x=148 to visually verify centring.
    d.hline(148, 80, 1)
    d.vline(148, 78, 5)
    # text_centered(s, cx, y) centres the string around cx.
    d.text_centered('centered@148', 148, 84)

    # text() is left-aligned; text_right(s, right_x, y) right-aligns.
    d.text('left-aligned', 2, 96)
    d.text_right('right@296', 296, 96)

    # -- Extended Latin characters --
    # The built-in fonts include _EXT tables for accented letters used
    # in Spanish and other Latin languages.
    d.text('ÁÉÍÓÚÑ áéíóúñ üÜ', 2, 108)
    d.text('¡Hola! ¿Cómo estás? Español', 2, 118)

    d.refresh()
    pause('Text Features')

    # =================================================================
    # PAGE 4 — Text Layout
    # Covers: text_in_rect() with align/valign/wrap options,
    #         text_wrapped(), badge(), mixed-font rendering
    # =================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 4: Text Layout', 4, 2, WHITE, font=font_medium)

    # -- text_in_rect alignment combos --
    # text_in_rect(s, x, y, w, h, color, align, valign, wrap, font, pad)
    #   align:  'left' | 'center' | 'right'
    #   valign: 'top'  | 'middle' | 'bottom'
    # Draw outline boxes first to show the bounding area.

    # Top-left aligned (default alignment).
    d.rect(2, 16, 90, 24)
    d.text_in_rect('top-left', 4, 18, 86, 20, align='left', valign='top')

    # Horizontally and vertically centred.
    d.rect(96, 16, 90, 24)
    d.text_in_rect('center-mid', 98, 18, 86, 20, align='center', valign='middle')

    # Right-aligned, bottom-aligned.
    d.rect(190, 16, 104, 24)
    d.text_in_rect('right-bot', 192, 18, 100, 20, align='right', valign='bottom')

    # -- Word wrap (text_wrapped) --
    # text_wrapped(s, x, y, max_width, color, font, line_spacing)
    # Breaks text at word boundaries to fit within max_width pixels.
    d.rect(2, 46, 140, 40)
    d.text_wrapped('This is a long sentence that should wrap within the box boundary.',
                   4, 48, 136)

    # -- text_in_rect with wrap=True --
    # When wrap=True, the text is word-wrapped AND aligned inside the rect.
    d.rect(148, 46, 140, 40)
    d.text_in_rect('Wrapped centered text in rect', 148, 46, 140, 40,
                   align='center', valign='middle', wrap=True)

    # -- Badges --
    # badge(s, x, y, color=BLACK, padding=2, font=None)
    # Draws an inverted-text label with a filled rounded-rect background.
    d.text('Badges:', 2, 92)
    d.badge('OK', 50, 90)
    d.badge('WARN', 75, 90)
    d.badge('ERROR', 115, 90)
    d.badge('v0.1', 165, 90)

    # -- Mixed fonts in one line --
    # Pass font= to individual text() calls to mix sizes without
    # changing the global default via set_font().
    d.text('Mixed:', 2, 108, font=font_medium)
    d.text('big', 60, 108, font=font_medium)
    d.text('+small', 90, 109)                  # default font_small
    d.text('=combo', 128, 108, font=font_medium)

    d.refresh()
    pause('Text Layout')

    # =================================================================
    # PAGE 5 — Widgets
    # Covers: bordered_panel(), progress_bar(), table(),
    #         divider() (solid/dashed/dotted), icon()
    # =================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 5: Widgets', 4, 2, WHITE, font=font_medium)

    # -- Bordered panels --
    # bordered_panel(x, y, w, h, title=None, color=BLACK, radius=0)
    # Panel A has rounded corners (radius=3); Panel B has sharp corners.
    d.bordered_panel(2, 15, 90, 40, title='Panel A', radius=3)
    d.text('content', 10, 32)

    d.bordered_panel(96, 15, 90, 40, title='Panel B')
    d.text('no radius', 104, 32)

    # -- Progress bars at 0%, 25%, 75%, 100% --
    # progress_bar(x, y, w, h, percent, color=BLACK)
    d.text('Progress:', 2, 60)
    d.progress_bar(60, 58, 80, 10, 0)
    d.text('0%', 144, 60)

    d.progress_bar(60, 72, 80, 10, 25)
    d.text('25%', 144, 74)

    d.progress_bar(60, 86, 80, 10, 75)
    d.text('75%', 144, 88)

    d.progress_bar(60, 100, 80, 10, 100)
    d.text('100%', 144, 102)

    # -- Table widget --
    # table(x, y, headers, rows, col_widths, color, font, row_height)
    d.table(190, 15, headers=['Name', 'Val'],
            rows=[['Temp', '23C'], ['Hum', '45%'], ['Volt', '3.3']],
            col_widths=[55, 45])

    # -- Divider styles comparison --
    d.text('dividers:', 190, 62)
    d.hline(190, 72, 100)                     # solid (hline shortcut)
    d.text('solid ^', 215, 74)
    d.dashed_line(190, 86, 290, 86)           # dashed
    d.text('dashed ^', 212, 88)
    d.dotted_line(190, 100, 290, 100)         # dotted
    d.text('dotted ^', 212, 102)

    # -- Bitmap icon --
    # icon(data, x, y, w=7, h=7, color=BLACK) draws a column-major
    # 1-bit bitmap.  Each byte is one column, LSB = top pixel.
    # This 7-byte star pattern is 7×7 pixels.
    star = b'\x08\x1c\x3e\x7f\x3e\x1c\x08'
    d.text('icon:', 190, 114)
    d.icon(star, 225, 114)                    # three stars in a row
    d.icon(star, 236, 114)
    d.icon(star, 247, 114)

    d.refresh()
    pause('Widgets')

    # =================================================================
    # PAGE 6 — Stress / Edge Cases
    # Covers: boundary drawing, corner text, tiny shapes,
    #         overlapping shapes, max text clipping, large shapes
    # =================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 6: Edge Cases', 4, 2, WHITE, font=font_medium)

    # -- Full-screen border --
    # Verifies rect() handles the exact display dimensions (296×128).
    d.rect(0, 0, 296, 128)
    d.text('top-left(0,12)', 1, 13)
    d.text_right('top-right', 295, 13)

    # -- Bottom corner text --
    # y=119 places text at the very bottom row (119 + 7 glyph = 126).
    d.text('bot-left', 1, 119)
    d.text_right('bot-right', 295, 119)

    # -- Tiny shapes --
    # Minimum viable sizes: radius 1–3 circles, 3×3 to 7×7 rects.
    d.text('tiny:', 2, 24)
    d.circle(45, 28, 1)
    d.circle(52, 28, 2)
    d.circle(62, 28, 3)
    d.rect(72, 25, 3, 3)
    d.rect(78, 25, 5, 5)
    d.rect(86, 25, 7, 7)

    # -- Overlapping shapes --
    # Three intersecting circles form a Venn-diagram pattern.
    d.text('overlap:', 2, 36)
    d.circle(55, 55, 12)
    d.circle(70, 55, 12)
    d.circle(62, 45, 12)

    # -- Fill + outline overlay --
    # Drawing a filled shape then the same shape as outline creates a
    # visible border around the filled area.
    d.text('fill+out:', 2, 68)
    d.circle(65, 82, 12, fill=True)
    d.circle(65, 82, 12)                      # outline over fill
    d.rect(83, 72, 25, 22, fill=True)
    d.rect(83, 72, 25, 22)                    # outline over fill

    # -- Max text length clipping --
    # 50 chars × 6 px = 300 px.  The display is 296 px wide, so the
    # last character is partially clipped by the display boundary.
    d.text('Max chars per line (5x7):', 2, 98)
    d.text('1234567890' * 5, 2, 108)

    # -- Large shapes in the right column --
    # Big circle (r=35), ellipse overlaid, and a thick diagonal line.
    d.text('large circ:', 160, 14)
    d.circle(220, 65, 35)
    d.ellipse(220, 65, 35, 25)
    d.line(185, 40, 255, 90, thickness=2)

    d.refresh()
    pause('Edge Cases')

    # =================================================================
    # PAGE 7 — 4-Grayscale
    # Covers: Display4Gray, fill_rect(), text(), hline(), refresh(),
    #         GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE
    # =================================================================
    # 4-gray uses a separate Display4Gray object with landscape orientation
    # (296×128) and GS2_HMSB framebuffer (2 bits per pixel, 4 gray levels).
    g = Display4Gray()
    g.clear()

    # Title
    g.text('PAGE 7: 4-GRAY', 8, 4, GRAY_BLACK)

    # -- Four gray bands (vertical strips across the width) --
    band_w = 60
    band_x = 8
    band_y = 18
    g.fill_rect(band_x, band_y, band_w, 50, GRAY_BLACK)
    g.text('BLACK', band_x + 4, band_y + 20, GRAY_WHITE)

    g.fill_rect(band_x + band_w, band_y, band_w, 50, GRAY_DARKGRAY)
    g.text('DARK', band_x + band_w + 4, band_y + 20, GRAY_LIGHTGRAY)

    g.fill_rect(band_x + band_w * 2, band_y, band_w, 50, GRAY_LIGHTGRAY)
    g.text('LIGHT', band_x + band_w * 2 + 4, band_y + 20, GRAY_DARKGRAY)

    g.fill_rect(band_x + band_w * 3, band_y, band_w, 50, GRAY_WHITE)
    g.text('WHITE', band_x + band_w * 3 + 4, band_y + 20, GRAY_BLACK)

    # -- Gradient bar (4 columns) --
    grad_y = 72
    g.text('Gradient:', 8, grad_y, GRAY_BLACK)
    colors_4g = [GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE]
    for i, c in enumerate(colors_4g):
        g.fill_rect(8 + i * 60, grad_y + 12, 60, 16, c)

    # -- Checkerboard --
    check_x = 8
    check_y = 102
    g.text('Check:', check_x, check_y, GRAY_BLACK)
    sq = 12
    for row in range(2):
        for col in range(16):
            g.fill_rect(check_x + 40 + col * sq, check_y + row * sq,
                        sq, sq, colors_4g[(row + col) % 4])

    g.refresh()
    # Re-init driver for 1-bit mode so the next loop iteration works
    g.reinit_mono()
    del g
    gc.collect()
    pause('4-Grayscale')

    # =================================================================
    # DONE — Summary screen before the next loop iteration
    # =================================================================
    d.clear()
    d.text_centered('ALL TESTS COMPLETE', 148, 42, font=font_medium)
    d.text_centered('7 pages rendered  |  loop ' + str(loop), 148, 58)
    gc.collect()
    d.text_centered('Free mem: ' + str(gc.mem_free()), 148, 72)
    d.text_centered('Restarting in 10s...', 148, 88)
    d.refresh()
    print('=== LOOP', loop, 'COMPLETE ===')
    print('Free mem:', gc.mem_free())
    time.sleep(10)  # pause before restarting the loop
