"""pico-paper-lib visual test suite.

Renders multiple test pages exercising every Display feature.
After each page the script pauses so the user can photograph the
display for visual review.

Upload to Pico and run:
    import test_all
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.fonts import font_small, font_medium
import time
import gc

d = Display()

def pause(label, seconds=8):
    """Show label on serial and wait for the display to be photographed."""
    print('--- PAGE:', label, '--- (waiting', seconds, 's)')
    gc.collect()
    print('Free mem:', gc.mem_free())
    time.sleep(seconds)

loop = 0

while True:
    loop += 1
    print('=== LOOP', loop, '===')

    # =====================================================================
    # PAGE 1 — Lines & Pixels
    # =====================================================================
    d.clear()

    # Title bar
    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 1: Lines & Pixels', 4, 2, WHITE, font=font_medium)

    y0 = 15

    # Thin line
    d.text('thin', 2, y0)
    d.line(40, y0 + 3, 140, y0 + 3)

    # Thick line
    d.text('thick(3)', 2, y0 + 10)
    d.line(55, y0 + 13, 140, y0 + 13, thickness=3)

    # Dashed line
    d.text('dashed', 2, y0 + 22)
    d.dashed_line(45, y0 + 25, 140, y0 + 25)

    # Dotted line
    d.text('dotted', 2, y0 + 32)
    d.dotted_line(45, y0 + 35, 140, y0 + 35)

    # Diagonal lines
    d.text('diag', 2, y0 + 44)
    d.line(40, y0 + 42, 80, y0 + 58)
    d.line(50, y0 + 42, 90, y0 + 58, thickness=2)

    # H/V lines
    d.text('h/v', 2, y0 + 62)
    d.hline(30, y0 + 65, 50)
    d.vline(100, y0 + 55, 20)

    # Pixels
    d.text('pixels', 2, y0 + 76)
    for i in range(10):
        d.pixel(40 + i * 4, y0 + 79)

    # Right half: cross-hatch pattern
    d.text('cross-hatch', 150, y0)
    for i in range(0, 60, 6):
        d.line(150, y0 + 10 + i, 210, y0 + 10 + i)
        d.line(150 + i, y0 + 10, 150 + i, y0 + 70)

    # Diagonal thick
    d.text('thick diag', 220, y0)
    d.line(220, y0 + 12, 285, y0 + 45, thickness=2)
    d.dashed_line(220, y0 + 50, 285, y0 + 80)

    # Dividers at bottom
    d.divider(118, style='solid')
    d.text('solid divider ^  dashed v', 80, 109)
    d.divider(126, style='dashed')

    d.refresh()
    pause('Lines & Pixels')

    # =====================================================================
    # PAGE 2 — Shapes
    # =====================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 2: Shapes', 4, 2, WHITE, font=font_medium)

    # Row 1: Rectangles
    d.text('rect', 2, 15)
    d.rect(2, 24, 30, 20)
    d.text('fill', 36, 15)
    d.rect(36, 24, 30, 20, fill=True)
    d.text('rounded', 72, 15)
    d.rounded_rect(72, 24, 40, 20, 5)
    d.text('rnd fill', 118, 15)
    d.rounded_rect(118, 24, 40, 20, 5, fill=True)

    # Row 2: Circles & Ellipses
    d.text('circle', 2, 50)
    d.circle(20, 68, 10)
    d.text('filled', 42, 50)
    d.circle(58, 68, 10, fill=True)
    d.text('ellipse', 78, 50)
    d.ellipse(108, 68, 16, 8)
    d.text('ell fill', 134, 50)
    d.ellipse(160, 68, 16, 8, fill=True)

    # Row 3: Triangles & Polygons
    d.text('tri', 2, 84)
    d.triangle(2, 124, 22, 96, 42, 124)
    d.text('tri fill', 48, 84)
    d.triangle(48, 124, 68, 96, 88, 124, fill=True)

    d.text('polygon', 100, 84)
    pts = [(104, 124), (114, 96), (134, 100), (144, 118), (124, 126)]
    d.polygon(pts)

    d.text('poly fill', 154, 84)
    pts2 = [(158, 124), (168, 96), (188, 100), (198, 118), (178, 126)]
    d.polygon(pts2, fill=True)

    # Right side: nested shapes
    d.text('nested', 210, 15)
    d.circle(245, 50, 25)
    d.circle(245, 50, 18)
    d.circle(245, 50, 11)
    d.circle(245, 50, 4, fill=True)

    d.text('concentric', 210, 84)
    d.rect(210, 94, 50, 30)
    d.rect(215, 99, 40, 20)
    d.rect(220, 104, 30, 10)

    d.refresh()
    pause('Shapes')

    # =====================================================================
    # PAGE 3 — Text Features
    # =====================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 3: Text', 4, 2, WHITE, font=font_medium)

    # Font comparison
    d.text('Small 5x7:', 2, 16)
    d.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 2, 26)
    d.text('abcdefghijklmnopqrstuvwxyz', 2, 36)
    d.text('0123456789 !@#$%^&*()', 2, 46)

    d.set_font(font_medium)
    d.text('Medium 8x8:', 2, 58)
    d.text('ABCDEFGHIJ 0123456789', 2, 68)
    d.set_font(font_small)

    # Alignment
    d.hline(148, 80, 1)  # center marker
    d.vline(148, 78, 5)
    d.text_centered('centered@148', 148, 84)

    d.text('left-aligned', 2, 96)
    d.text_right('right@296', 296, 96)

    # Spanish characters
    d.text('ÁÉÍÓÚÑ áéíóúñ üÜ', 2, 108)
    d.text('¡Hola! ¿Cómo estás? Español', 2, 118)

    d.refresh()
    pause('Text Features')

    # =====================================================================
    # PAGE 4 — Text Layout
    # =====================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 4: Text Layout', 4, 2, WHITE, font=font_medium)

    # text_in_rect with alignment combos (2px inner padding)
    d.rect(2, 16, 90, 24)
    d.text_in_rect('top-left', 4, 18, 86, 20, align='left', valign='top')

    d.rect(96, 16, 90, 24)
    d.text_in_rect('center-mid', 98, 18, 86, 20, align='center', valign='middle')

    d.rect(190, 16, 104, 24)
    d.text_in_rect('right-bot', 192, 18, 100, 20, align='right', valign='bottom')

    # Word wrap
    d.rect(2, 46, 140, 40)
    d.text_wrapped('This is a long sentence that should wrap within the box boundary.',
                   4, 48, 136)

    # text_in_rect with wrap
    d.rect(148, 46, 140, 40)
    d.text_in_rect('Wrapped centered text in rect', 148, 46, 140, 40,
                   align='center', valign='middle', wrap=True)

    # Badges
    d.text('Badges:', 2, 92)
    d.badge('OK', 50, 90)
    d.badge('WARN', 75, 90)
    d.badge('ERROR', 115, 90)
    d.badge('v0.1', 165, 90)

    # Mixed fonts in one line
    d.text('Mixed:', 2, 108, font=font_medium)
    d.text('big', 60, 108, font=font_medium)
    d.text('+small', 90, 109)
    d.text('=combo', 128, 108, font=font_medium)

    d.refresh()
    pause('Text Layout')

    # =====================================================================
    # PAGE 5 — Widgets
    # =====================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 5: Widgets', 4, 2, WHITE, font=font_medium)

    # Bordered panels
    d.bordered_panel(2, 15, 90, 40, title='Panel A', radius=3)
    d.text('content', 10, 32)

    d.bordered_panel(96, 15, 90, 40, title='Panel B')
    d.text('no radius', 104, 32)

    # Progress bars
    d.text('Progress:', 2, 60)
    d.progress_bar(60, 58, 80, 10, 0)
    d.text('0%', 144, 60)

    d.progress_bar(60, 72, 80, 10, 25)
    d.text('25%', 144, 74)

    d.progress_bar(60, 86, 80, 10, 75)
    d.text('75%', 144, 88)

    d.progress_bar(60, 100, 80, 10, 100)
    d.text('100%', 144, 102)

    # Table
    d.table(190, 15, headers=['Name', 'Val'],
            rows=[['Temp', '23C'], ['Hum', '45%'], ['Volt', '3.3']],
            col_widths=[55, 45])

    # Dividers
    d.text('dividers:', 190, 62)
    d.hline(190, 72, 100)
    d.text('solid ^', 215, 74)
    d.dashed_line(190, 86, 290, 86)
    d.text('dashed ^', 212, 88)
    d.dotted_line(190, 100, 290, 100)
    d.text('dotted ^', 212, 102)

    # Bitmap icon
    star = b'\x08\x1c\x3e\x7f\x3e\x1c\x08'
    d.text('icon:', 190, 114)
    d.icon(star, 225, 114)
    d.icon(star, 236, 114)
    d.icon(star, 247, 114)

    d.refresh()
    pause('Widgets')

    # =====================================================================
    # PAGE 6 — Stress / Edge Cases
    # =====================================================================
    d.clear()

    d.fill_rect(0, 0, 296, 11, BLACK)
    d.text('PAGE 6: Edge Cases', 4, 2, WHITE, font=font_medium)

    # Boundary drawing
    d.rect(0, 0, 296, 128)  # full-screen border
    d.text('top-left(0,12)', 1, 13)
    d.text_right('top-right', 295, 13)

    # Bottom corners
    d.text('bot-left', 1, 119)
    d.text_right('bot-right', 295, 119)

    # Tiny shapes
    d.text('tiny:', 2, 24)
    d.circle(45, 28, 1)
    d.circle(52, 28, 2)
    d.circle(62, 28, 3)
    d.rect(72, 25, 3, 3)
    d.rect(78, 25, 5, 5)
    d.rect(86, 25, 7, 7)

    # Overlapping shapes
    d.text('overlap:', 2, 36)
    d.circle(55, 55, 12)
    d.circle(70, 55, 12)
    d.circle(62, 45, 12)

    # Fill vs outline
    d.text('fill+out:', 2, 68)
    d.circle(65, 82, 12, fill=True)
    d.circle(65, 82, 12)
    d.rect(83, 72, 25, 22, fill=True)
    d.rect(83, 72, 25, 22)

    # Max text length
    d.text('Max chars per line (5x7):', 2, 98)
    d.text('1234567890' * 5, 2, 108)  # 50 chars, 300px — clips at 296

    # Right column: large shapes
    d.text('large circ:', 160, 14)
    d.circle(220, 65, 35)
    d.ellipse(220, 65, 35, 25)
    d.line(185, 40, 255, 90, thickness=2)

    d.refresh()
    pause('Edge Cases')

    # =====================================================================
    # DONE — summary before next loop
    # =====================================================================
    d.clear()
    d.text_centered('ALL TESTS COMPLETE', 148, 42, font=font_medium)
    d.text_centered('6 pages rendered  |  loop ' + str(loop), 148, 58)
    gc.collect()
    d.text_centered('Free mem: ' + str(gc.mem_free()), 148, 72)
    d.text_centered('Restarting in 10s...', 148, 88)
    d.refresh()
    print('=== LOOP', loop, 'COMPLETE ===')
    print('Free mem:', gc.mem_free())
    time.sleep(10)
