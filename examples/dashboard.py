"""
dashboard.py — Status dashboard demo with panels, badges, and tables.
"""

from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE
from pico_paper_lib.fonts import font_small, font_medium

d = Display()
d.clear()

# Title bar
d.fill_rect(0, 0, 296, 13, BLACK)
d.set_font(font_medium)
d.text('SYSTEM DASHBOARD', 4, 2, WHITE)
d.set_font(font_small)
d.text('10:30', 260, 3, WHITE)

# Left panel — metrics
d.bordered_panel(2, 18, 144, 60, title='Metrics')
y = 35
for label, val in [('CPU', '12%'), ('RAM', '45%'), ('Disk', '78%')]:
    d.text(label, 8, y)
    pct = int(val.strip('%'))
    d.progress_bar(40, y - 1, 60, 9, pct)
    d.text(val, 105, y)
    y += 14

# Right panel — alerts
d.bordered_panel(150, 18, 144, 60, title='Alerts')
d.text('All systems normal', 156, 40)
d.badge('OK', 260, 58)

# Bottom table
d.table(2, 84, 
    headers=['Service', 'Status', 'Uptime'],
    rows=[
        ['Web', 'Running', '14d'],
        ['DB', 'Running', '14d'],
        ['Cache', 'Warning', '2d'],
    ],
    col_widths=[100, 90, 100])

d.refresh()
print('Dashboard rendered.')
