# pico-paper-lib

A feature-rich MicroPython library for **Waveshare 2.9" e-paper displays** (SSD1680) on **Raspberry Pi Pico W**.

> Drop-in replacement for the basic Waveshare driver — adds graphics primitives, multi-font text with alignment, UI widgets, and a clean API.

## Features

| Category | What you get |
|---|---|
| **Display** | Full & partial refresh, 4-grayscale mode, sleep/wake, landscape & portrait |
| **Graphics** | Lines (thick, dashed, dotted), rectangles (rounded), circles, ellipses, triangles, polygons, bitmaps |
| **Text** | Two built-in fonts (5×7, 8×8), left/center/right alignment, word-wrap, text-in-rect |
| **Widgets** | Progress bar, table, bordered panel, badge/tag, dividers |
| **Extensible** | Add custom bitmap fonts, column-major or row-major icon bitmaps |

## Hardware

- **MCU**: Raspberry Pi Pico W (RP2040)
- **Display**: Waveshare 2.9" e-paper (296×128, SSD1680 controller)
- **Connection**: SPI (default pins: RST=12, DC=8, CS=9, BUSY=13)

## Quick Start

```python
from pico_paper_lib import Display

# Create display (landscape 296×128 by default)
d = Display()
d.clear()

# Draw some shapes
d.text('Hello Pico!', 10, 10)
d.circle(148, 64, 30, fill=True)
d.rounded_rect(200, 20, 80, 40, 5)
d.line(10, 120, 286, 120, thickness=2)

# Push to screen
d.refresh()

# Save power
d.sleep()
```

## Installation

### Option 1: `mip` (recommended)

Install directly on the Pico over WiFi:

```python
import mip
mip.install("github:jonbrefe/pico-paper-lib")
```

Or from the host via `mpremote`:

```bash
mpremote mip install github:jonbrefe/pico-paper-lib
```

### Option 2: Manual upload

Copy the `pico_paper_lib/` folder to your Pico's filesystem:

```
/pico_paper_lib/
    __init__.py
    driver.py
    display.py
    graphics.py
    fonts.py
```

Using [pico-ctl](https://github.com/jonbrefe/pico-ctl):

```bash
cd ../pico-ctl
python3 pico_ctl.py upload --dir ../pico-paper-lib /pico_paper_lib
```

Or use [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), Thonny, or any serial upload tool.

## API Reference

### Display

```python
from pico_paper_lib import Display
from pico_paper_lib.display import BLACK, WHITE, LANDSCAPE, PORTRAIT

d = Display(orientation=LANDSCAPE)
```

#### Canvas

| Method | Description |
|---|---|
| `d.clear(color=WHITE)` | Fill canvas with color |
| `d.refresh(full=True)` | Push canvas to display |
| `d.refresh_partial()` | Fast partial refresh |
| `d.sleep()` | Deep-sleep mode (<1 µA) |
| `d.wake()` | Wake and re-initialise |

#### 4-Grayscale Mode

The display supports a 4-level grayscale mode (black, dark gray, light gray, white) using a separate `Display4Gray` class. Supports both landscape (296×128, default) and portrait (128×296) orientations via the `orientation` parameter. Uses the `GS2_HMSB` framebuffer format.

```python
from pico_paper_lib import Display4Gray
from pico_paper_lib.display import GRAY_BLACK, GRAY_DARKGRAY, GRAY_LIGHTGRAY, GRAY_WHITE
from pico_paper_lib.display import LANDSCAPE, PORTRAIT

# Landscape (default) — 296×128
g = Display4Gray()
g.clear()
g.fill_rect(0, 0, 74, 128, GRAY_BLACK)
g.text('Hello 4-gray!', 80, 55, GRAY_BLACK)
g.refresh()
g.sleep()

# Portrait — 128×296
g = Display4Gray(orientation=PORTRAIT)
g.clear()
g.fill_rect(0, 0, 128, 74, GRAY_BLACK)
g.text('BLACK', 10, 33, GRAY_WHITE)
g.refresh()
g.sleep()
```

| Method | Description |
|---|---|
| `Display4Gray(orientation=LANDSCAPE, **pins)` | Create 4-gray canvas (landscape 296×128 by default) |
| `g.clear(color=GRAY_WHITE)` | Fill canvas with gray level |
| `g.fill_rect(x, y, w, h, color)` | Filled rectangle |
| `g.rect(x, y, w, h, color, fill)` | Rectangle (outline or filled) |
| `g.text(s, x, y, color, font)` | Left-aligned text |
| `g.text_centered(s, cx, y, color, font)` | Center text around cx |
| `g.text_right(s, right_x, y, color, font)` | Right-aligned text |
| `g.text_width(s, font)` | Measure string width in pixels |
| `g.set_font(font)` | Set default font |
| `g.icon(data, x, y, color)` | Draw 7×7 column-major bitmap icon |
| `g.badge(label, x, y, color)` | Inverted text badge |
| `g.line(x0, y0, x1, y1, color)` | Line |
| `g.hline(x, y, w, color)` | Horizontal line |
| `g.vline(x, y, h, color)` | Vertical line |
| `g.pixel(x, y, color)` | Single pixel |
| `g.refresh()` | Push to display (4-gray waveform, ~3s) |
| `g.reinit_mono()` | Return driver to 1-bit mode |
| `g.sleep()` / `g.wake()` | Power management |
| `g.framebuffer` | Access raw `framebuf.FrameBuffer` |
| `g.buffer` | Access raw byte buffer |

**Gray level constants:**

| Constant | Value | Appearance |
|---|---|---|
| `GRAY_BLACK` | `0x00` | Black |
| `GRAY_LIGHTGRAY` | `0x01` | Light gray |
| `GRAY_DARKGRAY` | `0x02` | Dark gray |
| `GRAY_WHITE` | `0x03` | White |

> **Note:** 4-gray mode uses full refresh only (no partial refresh).
> After using 4-gray, call `reinit_mono()` before switching back to a
> standard `Display` instance.

#### Drawing

| Method | Description |
|---|---|
| `d.pixel(x, y, color)` | Single pixel |
| `d.line(x0, y0, x1, y1, color, thickness)` | Line with optional thickness |
| `d.hline(x, y, w, color)` | Horizontal line |
| `d.vline(x, y, h, color)` | Vertical line |
| `d.dashed_line(x0, y0, x1, y1, color, dash, gap)` | Dashed line |
| `d.dotted_line(x0, y0, x1, y1, color, spacing)` | Dotted line |
| `d.rect(x, y, w, h, color, fill)` | Rectangle |
| `d.rounded_rect(x, y, w, h, r, color, fill)` | Rounded rectangle |
| `d.circle(cx, cy, r, color, fill)` | Circle |
| `d.ellipse(cx, cy, rx, ry, color, fill)` | Ellipse |
| `d.triangle(x0, y0, x1, y1, x2, y2, color, fill)` | Triangle |
| `d.polygon(points, color, fill)` | Polygon from (x,y) list |
| `d.bitmap(data, x, y, w, h, color, row_major)` | Bitmap icon |

#### Text

```python
from pico_paper_lib.fonts import font_small, font_medium

d.set_font(font_medium)               # switch to 8×8 font
d.text('Left aligned', 0, 0)
d.text_centered('Centered', 148, 20)
d.text_right('Right', 296, 40)
d.text_in_rect('Boxed', 10, 50, 100, 20, align='center', valign='middle', wrap=True)
d.text_wrapped('Long text here...', 10, 80, 200)
```

| Method | Description |
|---|---|
| `d.text(s, x, y, color, font)` | Left-aligned text |
| `d.text_centered(s, cx, y, color, font)` | Center around cx |
| `d.text_right(s, right_x, y, color, font)` | Right-aligned |
| `d.text_in_rect(s, x, y, w, h, ..., align, valign, wrap)` | Text in bounding box |
| `d.text_wrapped(s, x, y, max_width, color, font)` | Word-wrapped text |
| `d.text_width(s, font)` | Measure string width |
| `d.set_font(font)` | Set default font |

#### Widgets

```python
# Bordered panel with title
d.bordered_panel(5, 5, 140, 60, title='Status', radius=4)

# Progress bar
d.progress_bar(10, 80, 120, 12, percent=75)

# Full-width divider
d.divider(100, style='dashed')

# Inverted badge
d.badge('OK', 200, 10)

# Data table
d.table(5, 5,
    headers=['Name', 'Value'],
    rows=[['Temp', '23°C'], ['Hum', '45%']],
    col_widths=[80, 60])
```

### Custom Fonts

Extend `BitmapFont` to add your own:

```python
from pico_paper_lib.fonts import BitmapFont

class MyFont(BitmapFont):
    CHAR_W = 6
    CHAR_H = 10
    GAP = 1
    _FIRST = 32
    _LAST = 126
    _DATA = b'...'  # your glyph data

d.set_font(MyFont())
```

### Direct FrameBuffer Access

For advanced use, access the raw `framebuf.FrameBuffer`:

```python
fb = d.framebuffer
fb.scroll(10, 0)       # hardware scroll
fb.blit(other_fb, 0, 0)  # blit another buffer
```

## Pin Configuration

Override default pins at construction:

```python
d = Display(rst=12, dc=8, cs=9, busy=13, spi_id=1, baudrate=4_000_000)
```

## Examples

See the `examples/` folder:

- **hello_world.py** — Basic text and shapes
- **dashboard.py** — Status dashboard with panels and progress bars
- **fonts_demo.py** — All built-in fonts side by side
- **grayscale_demo.py** — 4-grayscale mode: gray bands, gradients, patterns
- **test_all.py** — Visual test suite: 7 pages covering every API feature

## Module Structure

```
pico_paper_lib/
├── __init__.py    — Package entry, exports Display
├── driver.py      — Low-level SSD1680 SPI driver
├── display.py     — High-level canvas (drawing + text + widgets)
├── graphics.py    — Geometry primitives (pure Python)
└── fonts.py       — BitmapFont base + Font5x7 + Font8x8
```

## Testing

`examples/test_all.py` is a visual test that renders 7 pages on the e-paper, covering lines, shapes, text, layout, widgets, edge cases, and 4-grayscale mode.

```bash
cd ../pico-ctl
python3 pico_ctl.py upload ../pico-paper-lib/examples/test_all.py /test_all.py
python3 pico_ctl.py run test_all.py
```

## Copilot Instructions

The `.github/copilot-instructions.md` file provides project-specific context to GitHub Copilot. It describes the target platform, code style conventions (pure MicroPython, column-major bitmaps, `const()` limitations), module architecture, and testing workflow. This helps Copilot generate code that is compatible with the Pico W hardware and MicroPython runtime.

## License

MIT License — see [LICENSE](LICENSE).

## Acknowledgements

The partial-refresh waveform lookup table (LUT) in `driver.py` is derived from the
[Waveshare Pico_CapTouch_ePaper](https://github.com/waveshareteam/Pico_CapTouch_ePaper)
example code, which carries an MIT license header in its source files.
Copyright (c) Waveshare team.

## Credits

- SSD1680 command reference from the [Waveshare Wiki](https://www.waveshare.com/wiki/Pico-CapTouch-ePaper-2.9)
- Font bitmaps derived from public-domain CP437 glyphs
