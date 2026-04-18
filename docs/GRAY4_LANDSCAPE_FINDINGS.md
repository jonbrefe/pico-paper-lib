# 4-Gray Landscape: Findings & Resolution

**Date:** 2026-04-18
**Status:** RESOLVED — landscape 4-gray mode working correctly

---

## Summary

The `gray4_update_landscape()` function in `driver.py` now correctly renders
4-grayscale images in landscape orientation (296×128). The fix was a single
change to the GS2_HMSB pixel extraction shift formula.

## Root Cause

The original code used shift `6 - ((py & 3) << 1)` to extract 2-bit pixel
values from the GS2_HMSB framebuffer, assuming pixel 0 was stored at the
MSB (bits 7:6) of each byte. Empirical testing on the Pico showed the
correct shift is `(py & 3) << 1`, which reverses the within-byte extraction
order and produces correctly oriented output.

**Fix applied in `gray4_update_landscape()`:**
```python
# Before (broken — text mirrored):
lx_shift = 6 - ((py & 3) << 1)

# After (working):
lx_shift = (py & 3) << 1
```

## What Was Tried (Chronological)

| # | Change | Result |
|---|--------|--------|
| 1 | Reverse X mapping (`lx = 295 - py`) | Still mirrored |
| 2 | Fix init sequence to match Waveshare C | No change |
| 3 | Swap gray constants to match wiki | Colors fixed, mirror persists |
| 4 | Remove stale `/lib/pico_paper_lib/` on Pico | Confirmed new code runs |
| 5 | Switch to mode 0x07 (column-major) | 90° rotation — wrong approach |
| 6 | Fix GS2_HMSB shift to `(py & 3) << 1` | **FIXED** |

## Key Discovery: Silent Upload Failures

A major debugging obstacle was that `pico_ctl upload` silently failed with
`MemoryError: memory allocation failed, allocating 8065 bytes` when the Pico
had modules loaded in memory. This meant many test iterations were actually
running OLD code. The workaround is to `machine.reset()` the Pico (and
reattach USB if using usbipd) before uploading large files.

## Architecture

- **Data entry mode 0x03** (row-major) — same as Waveshare C code
- **Init sequence** matches `EPD_2IN9_V2_Gray4_Init` exactly
- **Bit-plane encoding**: each gray level (2 bits) is split into two 1-bit
  planes sent to RAM 0x24 and RAM 0x26
- **Landscape rotation** is done pixel-by-pixel during the bit-plane
  conversion, iterating over portrait gate lines (py=0..295) and source
  bytes (px_byte=0..15)

## Gray Constants

| Constant | Value | Appearance |
|----------|-------|------------|
| `GRAY_BLACK` | 0x00 | Black |
| `GRAY_LIGHTGRAY` | 0x01 | Light gray |
| `GRAY_DARKGRAY` | 0x02 | Dark gray |
| `GRAY_WHITE` | 0x03 | White |
