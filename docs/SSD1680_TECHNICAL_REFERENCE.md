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

- 2 bits per pixel, horizontal MSB-first layout
- Each byte stores 4 pixels
- Pixel 0 (leftmost) = bits 7:6
- Pixel 1 = bits 5:4
- Pixel 2 = bits 3:2
- Pixel 3 (rightmost) = bits 1:0

Gray values:
| Value | Bits | Color |
|-------|------|-------|
| 0x00 | 00 | Black |
| 0x01 | 01 | Light gray |
| 0x02 | 10 | Dark gray |
| 0x03 | 11 | White |

For a 296×128 landscape buffer:
```
stride = 296 / 4 = 74 bytes per row
buf[ly * 74 + lx // 4]   → byte containing pixel at (lx, ly)
shift = 2 * (lx % 4)     → bit position within byte (empirically determined)
gray = (byte >> shift) & 3
```

> **Note:** The working shift formula `2 * (lx % 4)` was determined empirically
> on the Pico. The standard MicroPython GS2_HMSB documentation suggests
> `6 - 2 * (lx % 4)` (MSB-first), but only the LSB-first formula produces
> correct landscape output. See `docs/GRAY4_LANDSCAPE_FINDINGS.md` for details.

For a 128×296 portrait buffer:
```
stride = 128 / 4 = 32 bytes per row
buf[py * 32 + px // 4]   → byte containing pixel at (px, py)
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
SW_RESET → wait
ANALOG_BLOCK_CTRL (0x74): 0x54
DIGITAL_BLOCK_CTRL (0x7E): 0x3B
DRIVER_OUTPUT: [0x27, 0x01, 0x00]  (296 gates)
DATA_ENTRY_MODE: 0x11 = 0x03       (row-major)
SET_WINDOW: (0, 0, 127, 295)
BORDER_WAVEFORM (0x3C): 0x00
DISPLAY_UPDATE_CTRL: [0x00, 0x80]
SET_CURSOR: (0, 0)
WRITE_LUT_4GRAY (159 bytes: 153 LUT + gate/source voltages + VCOM)
```

### 4-Gray Display Update

After writing both planes (0x24 and 0x26):
```
DISPLAY_UPDATE_CTRL2 (0x22): 0xC7
MASTER_ACTIVATION (0x20)
wait for BUSY
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

None — all known issues have been resolved.

### 4-Gray Landscape (RESOLVED)

The landscape mirror issue was caused by using the wrong GS2_HMSB pixel
extraction shift. Changing from `6 - ((py & 3) << 1)` to `(py & 3) << 1`
in `gray4_update_landscape()` resolved the problem.
See `docs/GRAY4_LANDSCAPE_FINDINGS.md` for the full investigation.

## References

- [SSD1680 Datasheet](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
- [Waveshare C example code](https://github.com/waveshareteam/Pico_CapTouch_ePaper)
  — `EPD_2in9_V2.c`, `GUI_Paint.c`
- [Waveshare Wiki: 2.9" e-Paper Module](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
- [MicroPython framebuf docs](https://docs.micropython.org/en/latest/library/framebuf.html)
