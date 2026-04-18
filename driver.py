"""
Low-level SPI driver for Waveshare 2.9" e-paper (SSD1680 controller).

Handles hardware communication: SPI, reset, busy-wait, command/data protocol,
LUT programming, and full/partial display update sequences.

Designed for Raspberry Pi Pico W with MicroPython.
"""

import framebuf
import utime
from machine import Pin, SPI

# Native resolution (portrait orientation in hardware)
WIDTH = 128
HEIGHT = 296

# Default pin assignments (Waveshare Pico CapTouch ePaper)
_DEFAULT_PINS = {
    'rst': 12,
    'dc': 8,
    'cs': 9,
    'busy': 13,
    'spi_id': 1,
    'baudrate': 4_000_000,
}

# Partial-refresh waveform LUT for SSD1680.
# Derived from Waveshare Pico_CapTouch_ePaper example code (MIT license header).
# Original: https://github.com/waveshareteam/Pico_CapTouch_ePaper
# Copyright (c) Waveshare team
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

# 4-grayscale waveform LUT (159 bytes: 153 LUT + gate/source voltages + VCOM).
# Derived from Waveshare Pico_CapTouch_ePaper example code (MIT license header).
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
    0x24,0x22,0x22,0x22,0x23,0x32,0x00,0x00,0x00,
    0x22,0x17,0x41,0xAE,0x32,0x28,
])


class Driver:
    """Low-level hardware driver for SSD1680-based 2.9" e-paper."""

    def __init__(self, **kwargs):
        cfg = dict(_DEFAULT_PINS)
        cfg.update(kwargs)
        self.rst_pin = Pin(cfg['rst'], Pin.OUT)
        self.dc_pin = Pin(cfg['dc'], Pin.OUT)
        self.cs_pin = Pin(cfg['cs'], Pin.OUT)
        self.busy_pin = Pin(cfg['busy'], Pin.IN, Pin.PULL_UP)
        self.spi = SPI(cfg['spi_id'])
        self.spi.init(baudrate=cfg['baudrate'])
        self.width = WIDTH
        self.height = HEIGHT
        self._hw_init()

    # ------------------------------------------------------------------
    # Low-level SPI helpers
    # ------------------------------------------------------------------
    def _cmd(self, command):
        """Send a command byte."""
        self.dc_pin.value(0)
        self.cs_pin.value(0)
        self.spi.write(bytes([command]))
        self.cs_pin.value(1)

    def _data(self, data):
        """Send a single data byte."""
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(bytes([data]))
        self.cs_pin.value(1)

    def _data_buf(self, buf):
        """Send a buffer of bytes (memoryview-friendly)."""
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(buf)
        self.cs_pin.value(1)

    def _wait(self, timeout_ms=5000):
        """Block until BUSY pin goes low or timeout."""
        start = utime.ticks_ms()
        while self.busy_pin.value() == 1:
            if utime.ticks_diff(utime.ticks_ms(), start) > timeout_ms:
                break
            utime.sleep_ms(10)

    # ------------------------------------------------------------------
    # Hardware reset & init
    # ------------------------------------------------------------------
    def _reset(self):
        """Hardware reset: pulse RST pin high-low-high with timing delays."""
        self.rst_pin.value(1)
        utime.sleep_ms(50)
        self.rst_pin.value(0)
        utime.sleep_ms(2)
        self.rst_pin.value(1)
        utime.sleep_ms(50)

    def _hw_init(self):
        """Full hardware initialisation sequence."""
        self._reset()
        self._wait()
        self._cmd(0x12)          # SW_RESET
        self._wait()
        self._cmd(0x01)          # DRIVER_OUTPUT_CONTROL
        self._data(0x27)         # MUX = 295
        self._data(0x01)
        self._data(0x00)
        self._cmd(0x11)          # DATA_ENTRY_MODE
        self._data(0x07)         # X inc, Y inc
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._cmd(0x21)          # DISPLAY_UPDATE_CTRL
        self._data(0x00)
        self._data(0x80)
        self._set_cursor(0, 0)
        self._wait()

    def _set_window(self, x0, y0, x1, y1):
        """Set the RAM drawing area (registers 0x44 X-range, 0x45 Y-range)."""
        self._cmd(0x44)
        self._data((x0 >> 3) & 0xFF)
        self._data((x1 >> 3) & 0xFF)
        self._cmd(0x45)
        self._data(y0 & 0xFF)
        self._data((y0 >> 8) & 0xFF)
        self._data(y1 & 0xFF)
        self._data((y1 >> 8) & 0xFF)

    def _set_cursor(self, x, y):
        """Set the RAM write cursor position (registers 0x4E/0x4F)."""
        self._cmd(0x4E)
        self._data(x & 0xFF)
        self._cmd(0x4F)
        self._data(y & 0xFF)
        self._data((y >> 8) & 0xFF)
        self._wait()

    def _send_lut(self):
        """Write the partial-refresh waveform LUT to register 0x32."""
        self._cmd(0x32)
        for b in _LUT_PARTIAL:
            self._data(b)
        self._wait()

    def _send_lut_4gray(self):
        """Write 4-gray LUT + voltage settings (159 bytes total)."""
        self._cmd(0x32)
        for i in range(153):
            self._data(_LUT_4GRAY[i])
        self._wait()
        self._cmd(0x3F)
        self._data(_LUT_4GRAY[153])
        self._cmd(0x03)          # gate voltage
        self._data(_LUT_4GRAY[154])
        self._cmd(0x04)          # source voltage
        self._data(_LUT_4GRAY[155])   # VSH
        self._data(_LUT_4GRAY[156])   # VSH2
        self._data(_LUT_4GRAY[157])   # VSL
        self._cmd(0x2C)          # VCOM
        self._data(_LUT_4GRAY[158])

    def _hw_init_4gray(self):
        """Hardware init for 4-grayscale mode.

        Based on the working Waveshare C implementation (EPD_2IN9_V2_Gray4_Init).
        Always uses mode 0x03 (row-major) matching the C code.
        """
        self._reset()
        utime.sleep_ms(100)
        self._wait()
        self._cmd(0x12)          # SW_RESET
        self._wait()
        self._cmd(0x74)          # analog block control
        self._data(0x54)
        self._cmd(0x7E)          # digital block control
        self._data(0x3B)
        self._cmd(0x01)          # DRIVER_OUTPUT_CONTROL
        self._data(0x27)         # MUX = 295
        self._data(0x01)
        self._data(0x00)
        self._cmd(0x11)          # DATA_ENTRY_MODE
        self._data(0x03)         # X inc, Y inc, X-first (row-major)
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._cmd(0x3C)          # border waveform
        self._data(0x00)
        self._cmd(0x21)          # display update control
        self._data(0x00)
        self._data(0x80)
        self._set_cursor(0, 0)
        self._wait()
        self._send_lut_4gray()

    # ------------------------------------------------------------------
    # Image transfer helpers
    # ------------------------------------------------------------------
    def _write_image(self, buf):
        """Write pixel buffer to display RAM (landscape byte reorder)."""
        w8 = self.width // 8
        h = self.height
        self._cmd(0x24)
        for j in range(w8 - 1, -1, -1):
            for i in range(h):
                self._data(buf[i + j * h])

    # ------------------------------------------------------------------
    # Public refresh methods
    # ------------------------------------------------------------------
    def full_update(self, buf):
        """Full refresh — flashes display, best image quality."""
        self._write_image(buf)
        self._cmd(0x22)
        self._data(0xF7)
        self._cmd(0x20)
        self._wait()

    def full_update_base(self, buf):
        """Full refresh that also writes to the 'previous' RAM frame.

        Call this once before using ``partial_update`` to establish
        the base image that partial updates are diffed against.
        """
        self._cmd(0x24)
        w8 = self.width // 8
        h = self.height
        for j in range(w8 - 1, -1, -1):
            for i in range(h):
                self._data(buf[i + j * h])
        self._cmd(0x26)
        for j in range(w8 - 1, -1, -1):
            for i in range(h):
                self._data(buf[i + j * h])
        self._cmd(0x22)
        self._data(0xF7)
        self._cmd(0x20)
        self._wait()

    def partial_update(self, buf):
        """Partial refresh — fast, no flash, slight ghosting over time."""
        self.rst_pin.value(0)
        utime.sleep_ms(2)
        self.rst_pin.value(1)
        utime.sleep_ms(2)
        self._send_lut()
        self._cmd(0x37)
        for b in (0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00):
            self._data(b)
        self._cmd(0x3C)
        self._data(0x80)
        self._cmd(0x22)
        self._data(0xC0)
        self._cmd(0x20)
        self._wait()
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._set_cursor(0, 0)
        self._write_image(buf)
        self._cmd(0x22)
        self._data(0x0F)
        self._cmd(0x20)
        self._wait()

    def clear(self, color=0xFF):
        """Clear display RAM to *color* and full-refresh."""
        w8 = self.width // 8
        h = self.height
        self._cmd(0x24)
        for _ in range(w8 * h):
            self._data(color)
        self._cmd(0x22)
        self._data(0xF7)
        self._cmd(0x20)
        self._wait()

    def gray4_update(self, buf):
        """Display a 4-grayscale image.

        *buf* is a GS2_HMSB framebuffer (2 bits per pixel, 128×296 portrait).
        The 2bpp data is split into two 1bpp bit-planes written to RAM 0x24
        and 0x26 respectively.  Total raw size: 128×296/4 = 9472 bytes.

        Pixel encoding (GS2_HMSB):
          0x03 = white, 0x02 = light gray, 0x01 = dark gray, 0x00 = black

        Bit-plane conversion matches the Waveshare C implementation
        (EPD_2IN9_V2_4GrayDisplay) — MSB-first extraction from 2bpp buffer.
        """
        self._hw_init_4gray()
        total = self.height * self.width // 8  # 4736 output bytes (1bpp per plane)

        # --- Bit-plane 0 → RAM 0x24 ---
        self._cmd(0x24)
        for i in range(total):
            temp3 = 0
            for j in range(2):
                temp1 = buf[i * 2 + j]
                for k in range(2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00   # white
                    elif temp2 == 0x00:
                        temp3 |= 0x01   # black
                    elif temp2 == 0x80:
                        temp3 |= 0x01   # 10
                    else:
                        temp3 |= 0x00   # 01
                    temp3 <<= 1
                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x01
                    else:
                        temp3 |= 0x00
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self._data(temp3)

        # --- Bit-plane 1 → RAM 0x26 ---
        self._cmd(0x26)
        for i in range(total):
            temp3 = 0
            for j in range(2):
                temp1 = buf[i * 2 + j]
                for k in range(2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00   # white
                    elif temp2 == 0x00:
                        temp3 |= 0x01   # black
                    elif temp2 == 0x80:
                        temp3 |= 0x00   # 10
                    else:
                        temp3 |= 0x01   # 01
                    temp3 <<= 1
                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x00
                    else:
                        temp3 |= 0x01
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self._data(temp3)

        # Trigger 4-gray display update
        self._cmd(0x22)
        self._data(0xC7)
        self._cmd(0x20)
        self._wait()

    def gray4_update_landscape(self, buf):
        """Display a 4-gray image from a landscape (296×128) GS2_HMSB buffer.

        Uses data entry mode 0x03 (row-major, same as Waveshare C code).
        Rotates the landscape framebuffer to portrait during bit-plane
        conversion.

        Mode 0x03 RAM fill order:
          py=0..295 (gate lines), px_byte=0..15 (X bytes) per gate line.

        Mapping:  py → landscape X,  px_byte → landscape Y group.

        GS2_HMSB pixel order: pixel 0 at LSB (bits 1:0), so
        shift = 2 * (lx % 4), NOT 6 - 2*(lx%4).
        """
        self._hw_init_4gray()
        stride = self.height // 4  # 74 bytes per landscape row (296/4)

        # --- Bit-plane 0 → RAM 0x24 ---
        self._cmd(0x24)
        for py in range(self.height):           # 0..295 (gate lines)
            lx_byte = py >> 2                   # py // 4
            lx_shift = (py & 3) << 1            # 2*(py%4) — GS2_HMSB LSB-first
            for px_byte in range(self.width >> 3):  # 0..15
                out = 0
                ly_base = 127 - (px_byte << 3)  # 127 - px_byte*8
                for bit in range(8):
                    ly = ly_base - bit
                    gray = (buf[ly * stride + lx_byte] >> lx_shift) & 3
                    # Plane 0: set bit for black(0) and dark gray(2)
                    if gray == 0 or gray == 2:
                        out |= (0x80 >> bit)
                self._data(out)

        # --- Bit-plane 1 → RAM 0x26 ---
        self._cmd(0x26)
        for py in range(self.height):
            lx_byte = py >> 2
            lx_shift = (py & 3) << 1
            for px_byte in range(self.width >> 3):
                out = 0
                ly_base = 127 - (px_byte << 3)
                for bit in range(8):
                    ly = ly_base - bit
                    gray = (buf[ly * stride + lx_byte] >> lx_shift) & 3
                    # Plane 1: set bit for black(0) and light gray(1)
                    if gray == 0 or gray == 1:
                        out |= (0x80 >> bit)
                self._data(out)

        self._cmd(0x22)
        self._data(0xC7)
        self._cmd(0x20)
        self._wait()

    def reinit(self):
        """Re-init to standard 1-bit mode after using 4-gray mode."""
        self._hw_init()

    def sleep(self):
        """Enter deep-sleep mode (< 1 µA).  Call ``wake()`` to resume."""
        self._cmd(0x10)
        self._data(0x01)
        utime.sleep_ms(100)

    def wake(self):
        """Wake from deep sleep by performing a full hardware re-init."""
        self._hw_init()
