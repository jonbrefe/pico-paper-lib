# SSD1680 E-Paper Display — Technical Reference

Hardware reference for the Waveshare 2.9" e-paper (128×296, SSD1680 controller)
on Raspberry Pi Pico W. Written for both humans and AI assistants working on
this codebase.

---

## Physical Panel

| Property | Value |
|----------|-------|
| Controller | SSD1680 (Solomon Systech) |
| Resolution | 128 × 296 pixels |
| Source lines (X axis) | 128 (horizontal in portrait) |
| Gate lines (Y axis) | 296 (vertical in portrait) |
| Colors | Mono (black/white) or 4-gray (black, dark gray, light gray, white) |
| Interface | SPI (4-wire: MOSI, SCK, CS, DC) + RST + BUSY |
| Default Pico pins | RST=12, DC=8, CS=9, BUSY=13, SPI1 at 4 MHz |

### Wiring

| Signal | Pico GPIO | SPI1 Function | Direction |
|--------|-----------|---------------|----------|
| MOSI | GP11 | SPI1 TX | Pico → Display |
| SCK | GP10 | SPI1 SCK | Pico → Display |
| CS | GP9 | Directly driven (GPIO) | Pico → Display |
| DC | GP8 | Directly driven (GPIO) | Pico → Display |
| RST | GP12 | Directly driven (GPIO) | Pico → Display |
| BUSY | GP13 | Directly driven (GPIO) | Display → Pico |
| GND | GND | — | Common |
| VCC | 3V3 | — | Power |

> SPI1 is used because SPI0's default pins conflict with the Waveshare CapTouch
> board layout. MOSI/SCK are auto-assigned by `machine.SPI(1)`; CS is manually
> toggled via GPIO (not hardware CS).

## Coordinate System

The display's **native orientation is portrait**: 128 pixels wide, 296 tall.

```
Portrait (native)         Landscape (rotated 90° CCW)
┌───────────┐              ┌─────────────────────────────┐
│ X=0 X=127 │              │ lx=0                 lx=295 │
│ Y=0       │              │ ly=0                        │
│           │              │                             │
│           │              │ ly=127                      │
│ Y=295     │              └─────────────────────────────┘
└───────────┘                Width=296, Height=128
 Width=128
 Height=296
```

### Portrait ↔ Landscape Mapping

When the display is mounted landscape (cable on the right):
- Portrait X=0 (source 0) → landscape **bottom** (ly=127)
- Portrait X=127 (source 127) → landscape **top** (ly=0)
- Portrait Y=0 (gate 0) → landscape **left** (lx=0)
- Portrait Y=295 (gate 295) → landscape **right** (lx=295)

Therefore: `portrait_x = 127 - landscape_y`, `portrait_y = landscape_x`

## SPI Protocol

The SSD1680 uses a command/data protocol controlled by the DC pin:

| DC pin | Meaning |
|--------|---------|
| LOW | Command byte |
| HIGH | Data byte(s) |

All transfers are MSB-first. CS is active low.

### BUSY Pin

The BUSY pin is an **active-high output** from the display:

| BUSY state | Meaning |
|------------|--------|
| **HIGH (1)** | Display is busy — do NOT send commands |
| **LOW (0)** | Display is idle — ready for next command |

Poll with `Pin.PULL_UP` and wait for LOW after any reset, init, or display
update command. The driver uses a 5-second timeout with 10ms polling interval.

### Key Command Registers

| Cmd | Name | Description |
|-----|------|-------------|
| 0x12 | SW_RESET | Software reset. Wait for BUSY after. |
| 0x01 | DRIVER_OUTPUT | Gate count (MUX). Data: `[0x27, 0x01, 0x00]` = 296 lines. |
| 0x11 | DATA_ENTRY_MODE | Controls RAM scan direction. Critical register. |
| 0x44 | SET_RAM_X | X address range: `[x_start/8, x_end/8]` |
| 0x45 | SET_RAM_Y | Y address range: `[y_start_lo, y_start_hi, y_end_lo, y_end_hi]` |
| 0x4E | SET_RAM_X_CURSOR | Starting X byte position |
| 0x4F | SET_RAM_Y_CURSOR | Starting Y position (16-bit) |
| 0x24 | WRITE_RAM_BW | Write to B/W (or plane 0) RAM |
| 0x26 | WRITE_RAM_RED | Write to Red (or plane 1) RAM |
| 0x22 | DISPLAY_UPDATE_CTRL2 | Update sequence selector |
| 0x20 | MASTER_ACTIVATION | Trigger display update |
| 0x32 | WRITE_LUT | Load waveform look-up table |
| 0x10 | DEEP_SLEEP | Enter deep sleep mode |
| 0x74 | ANALOG_BLOCK_CTRL | Analog block control (4-gray: 0x54) |
| 0x7E | DIGITAL_BLOCK_CTRL | Digital block control (4-gray: 0x3B) |
| 0x3C | BORDER_WAVEFORM | Border waveform control |

## Data Entry Mode (Register 0x11) — CRITICAL

This register controls how the RAM address counter auto-increments when you
stream pixel data via command 0x24 or 0x26.

| Value | X dir | Y dir | Scan order | Used by |
|-------|-------|-------|------------|---------|
| 0x03 | increment | increment | **X-first (row-major)** | 4-gray init |
| 0x07 | increment | increment | **Y-first (column-major)** | Mono init |

### Mode 0x03 — Row-major (4-gray)

Data fills RAM row by row:
```
Byte 0..15:   Y=0,   X_byte=0..15  (16 bytes = 128 pixels)
Byte 16..31:  Y=1,   X_byte=0..15
...
Byte 4720..4735: Y=295, X_byte=0..15
Total: 296 × 16 = 4736 bytes per plane
```

### Mode 0x07 — Column-major (mono)

Data fills RAM column by column:
```
Byte 0..295:    X_byte=0,  Y=0..295
Byte 296..591:  X_byte=1,  Y=0..295
...
Byte 4440..4735: X_byte=15, Y=0..295
Total: 16 × 296 = 4736 bytes per plane
```

### Why this matters for landscape rotation

The mono driver (`_write_image`) sends data for mode 0x07 by iterating
`j=15..0` (X bytes, reversed), and for each j, `i=0..295` (Y values).
This maps the landscape framebuffer to portrait RAM correctly.

The 4-gray driver uses mode 0x03 and manually rotates pixel-by-pixel during
bit-plane conversion in `gray4_update_landscape()`.

## Framebuffer Formats

### MONO_VLSB (1-bit monochrome)

Used by the `Display` class. MicroPython's `framebuf.MONO_VLSB`.

- 1 bit per pixel, vertical byte layout
- Each byte represents 8 vertical pixels
- Bit 0 = top pixel, bit 7 = bottom pixel
- Buffer dimensions: (296, 128) for landscape logical view
- Buffer size: 296 × 128/8 = 4736 bytes

Layout for a 296×128 buffer:
```
buf[col + row_byte * 296]
  col = 0..295 (X in landscape)
  row_byte = 0..15 (Y/8 in landscape)
  bit within byte = Y % 8
```

### GS2_HMSB (2-bit 4-grayscale)

Used by the `Display4Gray` class. MicroPython's `framebuf.GS2_HMSB`.

- 2 bits per pixel, horizontal layout
- Each byte stores 4 pixels

**Byte layout (per MicroPython docs):**
```
Byte:  [P0_hi P0_lo] [P1_hi P1_lo] [P2_hi P2_lo] [P3_hi P3_lo]
Bits:     7     6       5     4       3     2       1     0
```
According to MicroPython documentation, GS2_HMSB is MSB-first: pixel 0 at
bits 7:6, pixel 3 at bits 1:0.

**However**, the shift formula that produces correct output on this
hardware is `shift = 2 * (x % 4)`, which reads pixel 0 from the LSB end.
This is the **opposite** of the documented MSB-first order.

We do not know why this reversal occurs (possible MicroPython build
difference, or RP2040-specific behavior). The important thing is:

```python
# CORRECT — use this to read pixel at (lx, ly) from a 296×128 landscape buffer:
stride = 296 // 4   # 74 bytes per row
byte_val = buf[ly * stride + lx // 4]
shift = 2 * (lx % 4)
gray = (byte_val >> shift) & 3
```

> **Do NOT use** `shift = 6 - 2*(lx%4)` — that produces mirrored output.

Gray values:

| Value | Bits | Color |
|-------|------|-------|
| 0x00 | 00 | Black |
| 0x01 | 01 | Light gray |
| 0x02 | 10 | Dark gray |
| 0x03 | 11 | White |

For a 128×296 portrait buffer:
```
stride = 128 // 4   # 32 bytes per row
byte_val = buf[py * stride + px // 4]
shift = 2 * (px % 4)
gray = (byte_val >> shift) & 3
```

## 4-Gray Bit-Plane Encoding

The SSD1680 uses two RAM planes (0x24 and 0x26) to encode 4 gray levels.
Each plane is 1-bit — the combination of both planes determines the gray level.

| Gray level | GS2 value | RAM 0x24 bit | RAM 0x26 bit |
|------------|-----------|-------------|-------------|
| White | 0x03 (11) | 0 | 0 |
| Dark gray | 0x02 (10) | 1 | 0 |
| Light gray | 0x01 (01) | 0 | 1 |
| Black | 0x00 (00) | 1 | 1 |

**Extraction from GS2_HMSB** (portrait, MSB-first — matches Waveshare C code):
```python
temp1 = buf[i * 2 + j]       # read byte from 2bpp buffer
temp2 = temp1 & 0xC0         # extract top 2 bits (MSB pixel)
# ... classify temp2 ...
temp1 <<= 2                  # shift to next pixel
```

This processes 4 pixels from each byte, MSB first, matching the GS2_HMSB layout.

## Initialization Sequences

### Standard Mono Init

```
SW_RESET → wait
DRIVER_OUTPUT: [0x27, 0x01, 0x00]  (296 gates)
DATA_ENTRY_MODE: 0x07               (column-major)
SET_WINDOW: (0, 0, 127, 295)
DISPLAY_UPDATE_CTRL: [0x00, 0x80]
SET_CURSOR: (0, 0)
```

### 4-Gray Init (from Waveshare C: EPD_2IN9_V2_Gray4_Init)

```
SW_RESET → wait BUSY
ANALOG_BLOCK_CTRL (cmd 0x74): data 0x54
DIGITAL_BLOCK_CTRL (cmd 0x7E): data 0x3B
DRIVER_OUTPUT (cmd 0x01): data [0x27, 0x01, 0x00]  (296 gates)
DATA_ENTRY_MODE (cmd 0x11): data 0x03  (row-major)
SET_WINDOW: (0, 0, 127, 295)
BORDER_WAVEFORM (cmd 0x3C): data 0x00
DISPLAY_UPDATE_CTRL (cmd 0x21): data [0x00, 0x80]
SET_CURSOR: (0, 0)
WRITE_LUT_4GRAY (159 bytes — see below)
```

### 4-Gray Display Update

After writing both planes (0x24 and 0x26):
```
DISPLAY_UPDATE_CTRL2 (cmd 0x22): data 0xC7
MASTER_ACTIVATION (cmd 0x20)
wait for BUSY → LOW
```

### 4-Gray Waveform LUT

The 4-gray LUT is 159 bytes total. The first 153 bytes go to register 0x32
(the waveform table). The remaining 6 bytes are written to separate voltage
registers:

```
Bytes 0–152:   → cmd 0x32 (WRITE_LUT) — waveform lookup table
Byte  153:     → cmd 0x3F — end option
Byte  154:     → cmd 0x03 — gate driving voltage
Bytes 155–157: → cmd 0x04 — source driving voltage (VSH, VSH2, VSL)
Byte  158:     → cmd 0x2C — VCOM voltage
```

The actual byte values (from Waveshare `EPD_2in9_V2.c`, MIT license):

```python
_LUT_4GRAY = bytes([
    0x00,0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x20,0x60,0x10,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x28,0x60,0x14,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x2A,0x60,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x90,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x02,0x00,0x05,0x14,0x00,0x00,
    0x1E,0x1E,0x00,0x00,0x00,0x00,0x01,
    0x00,0x02,0x00,0x05,0x14,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x24,0x22,0x22,0x22,0x23,0x32,0x00,0x00,0x00,  # gate/source timing
    0x22,0x17,0x41,0xAE,0x32,0x28,                  # 0x3F, 0x03, 0x04×3, 0x2C
])
```

### Partial Refresh Waveform LUT

Partial refresh uses a different waveform that avoids the full black/white
flash. Same structure: 153 bytes to 0x32, then 6 bytes to voltage registers.

**Prerequisites:** Call `full_update_base()` first to write the same image to
both RAM 0x24 (current) and RAM 0x26 (previous). The SSD1680 diffs these
two frames during partial refresh.

```python
_LUT_PARTIAL = bytes([
    0x00,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x80,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x40,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x0A,0x00,0x00,0x00,0x00,0x00,0x01,
    0x01,0x00,0x00,0x00,0x00,0x00,0x00,
    0x01,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x22,0x22,0x22,0x22,0x22,0x22,0x00,0x00,0x00,
    0x22,0x17,0x41,0xB0,0x32,0x36,
])
```

### Partial Refresh Flow

```
1. RST pin: LOW 2ms → HIGH 2ms  (soft hardware reset)
2. Load partial LUT (cmd 0x32)
3. cmd 0x37: data [0x00,0x00,0x00,0x00,0x00,0x40,0x00,0x00,0x00,0x00]
4. BORDER_WAVEFORM (cmd 0x3C): data 0x80
5. DISPLAY_UPDATE_CTRL2 (cmd 0x22): data 0xC0
6. MASTER_ACTIVATION (cmd 0x20) → wait BUSY
7. SET_WINDOW + SET_CURSOR (reset RAM pointers)
8. Write new image to RAM 0x24
9. DISPLAY_UPDATE_CTRL2 (cmd 0x22): data 0x0F
10. MASTER_ACTIVATION (cmd 0x20) → wait BUSY
```

> **Ghosting:** Partial refresh accumulates ghosting over time. Do a full
> refresh every 5–10 partial updates to clean the display.

## Deep Sleep & Wake

### Entering Deep Sleep

```
DEEP_SLEEP (cmd 0x10): data 0x01
wait 100ms
```

Power consumption drops to < 1 µA. All RAM contents are preserved but the
controller ignores all commands except a hardware reset.

### Waking from Deep Sleep

A full hardware re-init is required — there is no "light wake" command:

```
RST pin: HIGH 50ms → LOW 2ms → HIGH 50ms  (hardware reset)
Run the full init sequence (_hw_init or _hw_init_4gray)
```

In code: call `driver.wake()` which internally calls `_hw_init()`.

## Refresh Timing

| Refresh type | Duration | Flash | Use case |
|-------------|----------|-------|----------|
| Full refresh | ~2–3 seconds | Yes (black/white flash) | Best image quality, required periodically |
| Partial refresh | ~0.3–0.5 seconds | No | Fast updates, accumulates ghosting |
| 4-gray full refresh | ~3 seconds | Yes | Only option for 4-gray mode |

> 4-gray mode does **not** support partial refresh. Every 4-gray update is a
> full refresh.

## End-to-End: Drawing a Pixel to Screen

Here's the complete flow from "I want to draw something" to "I see it":

### Mono (1-bit)

```python
from pico_paper_lib import Display

d = Display()                      # 1. Init SPI + SSD1680 (mode 0x07)
d.clear()                          # 2. Fill framebuffer with WHITE
d.pixel(10, 10, 0)                 # 3. Set pixel in MONO_VLSB framebuffer
d.text('Hello', 20, 20)            # 4. Draw text into framebuffer
d.refresh()                        # 5. _write_image: rotate bytes, send to
                                   #    RAM 0x24, trigger 0xF7 update
d.sleep()                          # 6. cmd 0x10 → deep sleep
```

### 4-Gray

```python
from pico_paper_lib import Display4Gray
from pico_paper_lib.display import GRAY_BLACK, GRAY_DARKGRAY, GRAY_WHITE

g = Display4Gray()                 # 1. Alloc GS2_HMSB framebuffer (296×128)
g.clear()                          # 2. Fill with GRAY_WHITE
g.fill_rect(0, 0, 74, 128, GRAY_BLACK)   # 3. Draw into framebuffer
g.text('Hello 4-gray!', 80, 55, GRAY_DARKGRAY)
g.refresh()                        # 4. _hw_init_4gray: re-init to mode 0x03,
                                   #    load 4-gray LUT
                                   # 5. gray4_update_landscape: extract 2-bit
                                   #    pixels, split into bit-planes,
                                   #    rotate to portrait, send to
                                   #    RAM 0x24 + 0x26
                                   # 6. Trigger 0xC7 update → wait BUSY
g.sleep()
```

### Partial Refresh

```python
d = Display()
d.clear()
d.text('Base image', 10, 10)
d.refresh(full=True)               # 1. full_update_base: writes to BOTH
                                   #    RAM 0x24 and 0x26 (sets reference)
# ... later ...
d.text('Updated', 10, 30)
d.refresh(full=False)              # 2. partial_update: load partial LUT,
                                   #    write only to RAM 0x24, trigger
                                   #    0x0F update (diffs against 0x26)
```

## Mono Landscape Byte Reorder

The `_write_image` method performs landscape → portrait rotation at the byte
level. This works because MONO_VLSB's vertical byte layout aligns with the
column-major scan of mode 0x07.

```python
def _write_image(self, buf):
    w8 = self.width // 8   # 16
    h = self.height         # 296
    self._cmd(0x24)
    for j in range(w8 - 1, -1, -1):    # j = 15, 14, ..., 0
        for i in range(h):              # i = 0, 1, ..., 295
            self._data(buf[i + j * h])
```

- `j=15` sent first → goes to RAM X_byte=0 (portrait left = landscape bottom)
- `j=0` sent last → goes to RAM X_byte=15 (portrait right = landscape top)
- `i=0..295` → RAM Y=0..295 (portrait top-to-bottom = landscape left-to-right)

Each byte in MONO_VLSB contains 8 vertical pixels. In landscape, these become
8 horizontal pixels in portrait, which is exactly one X byte in the RAM.

## Known Issues

None.

## References

- [SSD1680 Datasheet](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
- [Waveshare C example code](https://github.com/waveshareteam/Pico_CapTouch_ePaper)
  — `EPD_2in9_V2.c`, `GUI_Paint.c`
- [Waveshare Wiki: 2.9" e-Paper Module](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
- [MicroPython framebuf docs](https://docs.micropython.org/en/latest/library/framebuf.html)
