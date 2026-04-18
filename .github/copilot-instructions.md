# Project Guidelines

## Overview

MicroPython library for **Waveshare 2.9" e-paper displays** (SSD1680 controller) on **Raspberry Pi Pico W**.
Provides a high-level `Display` class wrapping a low-level SPI driver, geometry primitives, bitmap fonts, and UI widgets.

## Target Platform

- **Runtime**: MicroPython v1.28.0+ on RP2040 (Pico W)
- **Display**: 296×128 px monochrome, SSD1680 controller, SPI interface
- **Pins (default)**: RST=12, DC=8, CS=9, BUSY=13, SPI ID=1

## Code Style

- Pure MicroPython — no CPython-only features
- No `from micropython import const` across module boundaries — `const()` values are NOT importable between modules. Use plain integer variables for cross-module constants.
- Column-major bitmap format: each byte = one column, LSB = top row
- Every public function and class must have a docstring
- Private helpers (prefix `_`) should still have a one-line docstring describing the algorithm

## Architecture

```
__init__.py   → Package entry, exports Display
driver.py     → Low-level SSD1680 SPI protocol (registers, LUT, refresh)
display.py    → High-level canvas: drawing, text, widgets (wraps Driver + FrameBuffer)
graphics.py   → Pure geometry primitives (Bresenham circle, scanline fill, etc.)
fonts.py      → BitmapFont base class + Font5x7 + Font8x8 with Spanish char support
examples/     → Standalone demos (hello_world, dashboard, fonts_demo)
package.json  → mip manifest for installing via mip.install("github:jonbrefe/pico-paper-lib")
```

- `display.py` depends on `driver.py`, `graphics.py`, and `fonts.py`
- `graphics.py` and `fonts.py` are independent of each other
- `driver.py` talks directly to hardware (SPI, GPIO)

## Conventions

- Display orientation: landscape (296 wide × 128 tall) by default
- Color values: `BLACK = 0x00`, `WHITE = 0xFF`
- Font glyphs for accented/Spanish characters go in `_EXT` dict on the font class, keyed by Unicode codepoint
- Partial refresh requires calling `full_update_base()` first to set the reference frame
- Memory is precious (~163KB free after loading). Avoid unnecessary allocations; prefer in-place operations.

## Installation

Install via `mip` (recommended):

```bash
# From pico-ctl/
python3 pico_ctl.py mip github:jonbrefe/pico-paper-lib
```

Or on the Pico directly:

```python
import mip
mip.install("github:jonbrefe/pico-paper-lib")
```

## Testing

There is no automated test suite. The `test_all.py` file is a visual test that renders 6 pages on the e-paper display.

Test by uploading to a Pico W using [pico-ctl](../pico-ctl):

```bash
cd ../pico-ctl
python3 pico_ctl.py upload --dir ../pico-paper-lib /pico_paper_lib
python3 pico_ctl.py upload ../pico-paper-lib/test_all.py /test_all.py
python3 pico_ctl.py run test_all.py
```

## License

MIT — Jonathan Brenes
