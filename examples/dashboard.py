"""
dashboard.py — System-status dashboard example using high-level widgets.

Demonstrates:
  - fill_rect() for an inverted (white-on-black) title bar
  - bordered_panel() with an optional title string
  - progress_bar() at various percentages
  - badge() — small inverted-text labels (e.g. "OK", "WARN")
  - table() — header row + data rows with fixed column widths
  - Mixing font_small and font_medium in one layout

Layout (296×128 landscape):
  ┌───────────── SYSTEM DASHBOARD ─────── 10:30 ┐  y 0–12
  │ ┌─ Metrics ──────┐ ┌─ Alerts ───────┐      │  y 18–77
  │ │ CPU  ████░ 12%  │ │ All systems OK │      │
  │ │ RAM  ████░ 45%  │ │           [OK] │      │
  │ │ Disk ████░ 78%  │ └────────────────┘      │
  │ └────────────────┘                          │
  │ ┌ Service ─┬ Status ──┬ Uptime ──┐          │  y 84–127
  │ │ Web      │ Running  │ 14d      │          │
  │ │ DB       │ Running  │ 14d      │          │
  │ │ Cache    │ Warning  │ 2d       │          │
  │ └──────────┴──────────┴──────────┘          │
  └─────────────────────────────────────────────┘

Upload & run:
  pico_ctl upload examples/dashboard.py /dashboard.py
  pico_ctl run dashboard.py
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.fonts import font_small, font_medium

# --- Initialise display (landscape 296×128) ---
d = Display()
d.clear()

# ---- Title bar ----
# Draw a solid black rectangle across the top, then render white text on it.
# fill_rect(x, y, w, h, color) fills a rectangle with the given colour.
d.fill_rect(0, 0, 296, 13, BLACK)
d.set_font(font_medium)
d.text('SYSTEM DASHBOARD', 4, 2, WHITE)        # left-aligned title
d.set_font(font_small)
d.text('10:30', 260, 3, WHITE)                  # right-aligned clock

# ---- Left panel: Metrics ----
# bordered_panel(x, y, w, h, title=None, color=BLACK, radius=0)
# Draws a rectangular border with an optional inset title string.
d.bordered_panel(2, 18, 144, 60, title='Metrics')

y = 35  # starting y for the first metric row
for label, val in [('CPU', '12%'), ('RAM', '45%'), ('Disk', '78%')]:
    d.text(label, 8, y)                         # metric name
    pct = int(val.strip('%'))
    # progress_bar(x, y, w, h, percent) — filled bar proportional to %.
    d.progress_bar(40, y - 1, 60, 9, pct)
    d.text(val, 105, y)                         # numeric value
    y += 14                                     # row spacing

# ---- Right panel: Alerts ----
d.bordered_panel(150, 18, 144, 60, title='Alerts')
d.text('All systems normal', 156, 40)
# badge(s, x, y, color=BLACK, padding=2, font=None)
# Renders text on an inverted (filled) rounded rectangle — like a tag.
d.badge('OK', 260, 58)

# ---- Bottom table ----
# table(x, y, headers, rows, col_widths, color=BLACK, font=None, row_height=None)
# Draws a grid with a header row and data rows.  col_widths sets each
# column's pixel width; row_height auto-sizes to the font if omitted.
d.table(2, 84,
    headers=['Service', 'Status', 'Uptime'],
    rows=[
        ['Web', 'Running', '14d'],
        ['DB', 'Running', '14d'],
        ['Cache', 'Warning', '2d'],
    ],
    col_widths=[100, 90, 100])

# ---- Push framebuffer to the e-paper ----
d.refresh()
print('Dashboard rendered.')
