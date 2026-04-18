"""
Minimal 4-gray pixel mapping test.

Draws asymmetric shapes that cannot be confused when mirrored:
  - A thick "F" shape in the top-left quadrant (unmistakable orientation)
  - A single-pixel-wide line from top-left corner going right
  - A single-pixel-wide line from top-left corner going down
  - A small black square at ONLY the top-left corner
"""

from pico_paper_lib.display import (
    Display4Gray,
    GRAY_BLACK, GRAY_WHITE,
)
import gc

g = Display4Gray()
g.clear()

# Big thick "F" shape — unmistakable orientation
# Vertical bar: x=10..20, y=10..70 (left spine)
g.fill_rect(10, 10, 10, 60, GRAY_BLACK)
# Top horizontal bar: x=10..60, y=10..20
g.fill_rect(10, 10, 50, 10, GRAY_BLACK)
# Middle horizontal bar: x=10..45, y=35..45
g.fill_rect(10, 35, 35, 10, GRAY_BLACK)

# 1px line from (0,0) going RIGHT, 100px long
g.hline(0, 0, 100, GRAY_BLACK)
# 1px line from (0,0) going DOWN, 50px tall
g.vline(0, 0, 50, GRAY_BLACK)

# Small 5x5 black square at top-left only
g.fill_rect(0, 0, 5, 5, GRAY_BLACK)

print('Refreshing F-test...')
g.refresh()
gc.collect()
print('Free mem:', gc.mem_free())
print('F-test complete.')
