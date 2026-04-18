"""
High-level Display canvas — the main entry point for the library.

Wraps the low-level Driver with a ``framebuf.FrameBuffer`` and exposes
drawing, text, and refresh helpers in a single convenient object.
"""

import framebuf
from .driver import Driver, WIDTH, HEIGHT
from .fonts import font_small, font_medium, BitmapFont
from . import graphics as gfx

# Logical orientation constants
LANDSCAPE = 0   # 296 x 128 (default)
PORTRAIT = 1    # 128 x 296

# Colour aliases for monochrome
BLACK = 0x00
WHITE = 0xFF

# Colour aliases for 4-grayscale mode (GS2_HMSB encoding)
# Wiki: Black=00, Light Grey=01, Dark Grey=10, White=11
GRAY_BLACK = 0x00
GRAY_LIGHTGRAY = 0x01
GRAY_DARKGRAY = 0x02
GRAY_WHITE = 0x03


class Display:
    """High-level e-paper canvas.

    Usage::

        from pico_paper_lib import Display

        d = Display()                 # landscape by default
        d.clear()
        d.text('Hello!', 10, 10)
        d.circle(148, 64, 30, fill=True)
        d.refresh()
        d.sleep()
    """

    def __init__(self, orientation=LANDSCAPE, **pin_kwargs):
        self._drv = Driver(**pin_kwargs)
        self._orientation = orientation
        if orientation == LANDSCAPE:
            self.width = HEIGHT   # 296
            self.height = WIDTH   # 128
        else:
            self.width = WIDTH    # 128
            self.height = HEIGHT  # 296
        self._buf = bytearray(HEIGHT * WIDTH // 8)
        self._fb = framebuf.FrameBuffer(
            self._buf, HEIGHT, WIDTH, framebuf.MONO_VLSB
        )
        self._font = font_small
        self._base_set = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def framebuffer(self):
        """Direct access to the underlying FrameBuffer for advanced use."""
        return self._fb

    @property
    def buffer(self):
        """Raw byte buffer backing the framebuffer."""
        return self._buf

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, f):
        if isinstance(f, BitmapFont):
            self._font = f

    # ------------------------------------------------------------------
    # Canvas operations
    # ------------------------------------------------------------------
    def clear(self, color=WHITE):
        """Fill the entire canvas with *color*."""
        self._fb.fill(color)

    def fill(self, color):
        """Alias for clear — fill canvas with *color*."""
        self._fb.fill(color)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    def refresh(self, full=True):
        """Push the canvas to the display.

        full=True  → full refresh (flashes, best quality)
        full=False → partial refresh (fast, may ghost over time)
        """
        if full:
            if not self._base_set:
                self._drv.full_update_base(self._buf)
                self._base_set = True
            else:
                self._drv.full_update(self._buf)
        else:
            if not self._base_set:
                self._drv.full_update_base(self._buf)
                self._base_set = True
            else:
                self._drv.partial_update(self._buf)

    def refresh_full(self):
        """Explicit full refresh."""
        self.refresh(full=True)

    def refresh_partial(self):
        """Explicit partial refresh (fast, slight ghosting)."""
        self.refresh(full=False)

    def sleep(self):
        """Put the e-paper into deep-sleep mode."""
        self._drv.sleep()

    def wake(self):
        """Wake from deep-sleep and re-initialise the hardware."""
        self._drv.wake()

    # ------------------------------------------------------------------
    # Pixel
    # ------------------------------------------------------------------
    def pixel(self, x, y, color=BLACK):
        """Set a single pixel."""
        self._fb.pixel(x, y, color)

    def get_pixel(self, x, y):
        """Read the color value of a single pixel."""
        return self._fb.pixel(x, y)

    # ------------------------------------------------------------------
    # Lines
    # ------------------------------------------------------------------
    def line(self, x0, y0, x1, y1, color=BLACK, thickness=1):
        """Draw a line, optionally with *thickness* > 1."""
        if thickness <= 1:
            self._fb.line(x0, y0, x1, y1, color)
        else:
            gfx.thick_line(self._fb, x0, y0, x1, y1, color, thickness)

    def hline(self, x, y, w, color=BLACK):
        """Draw a horizontal line of width *w* pixels."""
        self._fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=BLACK):
        """Draw a vertical line of height *h* pixels."""
        self._fb.vline(x, y, h, color)

    def dashed_line(self, x0, y0, x1, y1, color=BLACK, dash=4, gap=3):
        gfx.dashed_line(self._fb, x0, y0, x1, y1, color, dash, gap)

    def dotted_line(self, x0, y0, x1, y1, color=BLACK, spacing=3):
        gfx.dotted_line(self._fb, x0, y0, x1, y1, color, spacing)

    # ------------------------------------------------------------------
    # Rectangles
    # ------------------------------------------------------------------
    def rect(self, x, y, w, h, color=BLACK, fill=False):
        """Draw a rectangle (outline or filled)."""
        gfx.rect(self._fb, x, y, w, h, color, fill)

    def fill_rect(self, x, y, w, h, color=BLACK):
        """Draw a filled rectangle."""
        self._fb.fill_rect(x, y, w, h, color)

    def rounded_rect(self, x, y, w, h, r, color=BLACK, fill=False):
        gfx.rounded_rect(self._fb, x, y, w, h, r, color, fill)

    # ------------------------------------------------------------------
    # Circles & ellipses
    # ------------------------------------------------------------------
    def circle(self, cx, cy, r, color=BLACK, fill=False):
        """Draw a circle centered at (*cx*, *cy*) with radius *r*."""
        gfx.circle(self._fb, cx, cy, r, color, fill)

    def ellipse(self, cx, cy, rx, ry, color=BLACK, fill=False):
        """Draw an ellipse with radii *rx* and *ry*."""
        gfx.ellipse(self._fb, cx, cy, rx, ry, color, fill)

    # ------------------------------------------------------------------
    # Triangles & polygons
    # ------------------------------------------------------------------
    def triangle(self, x0, y0, x1, y1, x2, y2, color=BLACK, fill=False):
        """Draw a triangle from three vertices."""
        gfx.triangle(self._fb, x0, y0, x1, y1, x2, y2, color, fill)

    def polygon(self, points, color=BLACK, fill=False):
        """Draw a polygon from a list of (x, y) tuples."""
        gfx.polygon(self._fb, points, color, fill)

    # ------------------------------------------------------------------
    # Bitmaps
    # ------------------------------------------------------------------
    def bitmap(self, data, x, y, w, h, color=BLACK, row_major=False):
        """Draw a bitmap image at (x, y). Column-major by default."""
        if row_major:
            gfx.bitmap_row_major(self._fb, data, x, y, w, h, color)
        else:
            gfx.bitmap_col_major(self._fb, data, x, y, w, h, color)

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------
    def text(self, s, x, y, color=BLACK, font=None):
        """Draw text at (x, y) using the current or specified font."""
        f = font or self._font
        f.draw_text(self._fb, s, x, y, color)

    def text_centered(self, s, cx, y, color=BLACK, font=None):
        """Draw text horizontally centered around *cx*."""
        f = font or self._font
        f.draw_text_centered(self._fb, s, cx, y, color)

    def text_right(self, s, right_x, y, color=BLACK, font=None):
        """Draw text right-aligned at *right_x*."""
        f = font or self._font
        f.draw_text_right(self._fb, s, right_x, y, color)

    def text_in_rect(self, s, x, y, w, h, color=BLACK,
                     align='left', valign='top', wrap=False, font=None, pad=4):
        """Draw text inside a bounding rectangle with alignment."""
        f = font or self._font
        f.draw_text_in_rect(self._fb, s, x, y, w, h, color, align, valign, wrap, pad)

    def text_wrapped(self, s, x, y, max_width, color=BLACK,
                     font=None, line_spacing=1):
        """Draw word-wrapped text."""
        f = font or self._font
        return f.draw_text_wrapped(self._fb, s, x, y, max_width, color, line_spacing)

    def text_width(self, s, font=None):
        """Return pixel width of string *s*."""
        f = font or self._font
        return f.text_width(s)

    def set_font(self, font):
        """Set the default font for subsequent text calls."""
        self._font = font

    # ------------------------------------------------------------------
    # Compound drawing helpers
    # ------------------------------------------------------------------
    def bordered_panel(self, x, y, w, h, title=None, color=BLACK, radius=0):
        """Draw a panel with optional rounded border and title bar."""
        if radius:
            self.rounded_rect(x, y, w, h, radius, color)
        else:
            self.rect(x, y, w, h, color)
        if title:
            title_h = self._font.CHAR_H + 4
            self.fill_rect(x + 1, y + 1, w - 2, title_h, color)
            # Inverted text for title
            inv = WHITE if color == BLACK else BLACK
            self._font.draw_text_in_rect(
                self._fb, title,
                x + 2, y + 2, w - 4, title_h,
                inv, align='center', valign='middle', pad=0
            )
            self.hline(x, y + title_h + 1, w, color)

    def progress_bar(self, x, y, w, h, percent, color=BLACK):
        """Draw a progress bar (0-100%)."""
        percent = max(0, min(100, percent))
        self.rect(x, y, w, h, color)
        fill_w = (w - 2) * percent // 100
        if fill_w > 0:
            self.fill_rect(x + 1, y + 1, fill_w, h - 2, color)

    def divider(self, y, color=BLACK, style='solid'):
        """Draw a full-width horizontal divider."""
        if style == 'dashed':
            self.dashed_line(0, y, self.width - 1, y, color)
        elif style == 'dotted':
            self.dotted_line(0, y, self.width - 1, y, color)
        else:
            self.hline(0, y, self.width, color)

    def table(self, x, y, headers, rows, col_widths, color=BLACK,
              font=None, row_height=None):
        """Draw a simple table with headers and data rows.

        *col_widths* is a list of pixel widths for each column.
        *rows* is a list of lists of strings.
        """
        f = font or self._font
        rh = row_height or (f.CHAR_H + 3)
        total_w = sum(col_widths)

        # Header row
        self.fill_rect(x, y, total_w, rh, color)
        inv = WHITE if color == BLACK else BLACK
        cx = x
        for i, hdr in enumerate(headers):
            f.draw_text_in_rect(
                self._fb, hdr, cx + 1, y, col_widths[i] - 2, rh,
                inv, align='center', valign='middle'
            )
            cx += col_widths[i]
        y += rh

        # Data rows
        for row_data in rows:
            cx = x
            for i, cell in enumerate(row_data):
                cw = col_widths[i] if i < len(col_widths) else col_widths[-1]
                f.draw_text_in_rect(
                    self._fb, str(cell), cx + 3, y, cw - 6, rh,
                    color, align='left', valign='middle'
                )
                cx += cw
            y += rh
            self.hline(x, y - 1, total_w, color)

        # Vertical column separators
        cx = x
        for cw in col_widths:
            self.vline(cx, y - rh * (len(rows) + 1), rh * (len(rows) + 1), color)
            cx += cw
        self.vline(cx, y - rh * (len(rows) + 1), rh * (len(rows) + 1), color)

    def badge(self, s, x, y, color=BLACK, padding=2, font=None):
        """Draw a text badge (inverted text in a rounded rectangle)."""
        f = font or self._font
        tw = f.text_width(s)
        th = f.CHAR_H
        bw = tw + padding * 2
        bh = th + padding * 2
        r = min(3, bh // 2)
        self.rounded_rect(x, y, bw, bh, r, color, fill=True)
        inv = WHITE if color == BLACK else BLACK
        f.draw_text(self._fb, s, x + padding, y + padding, inv)

    def icon(self, data, x, y, w=7, h=7, color=BLACK):
        """Draw a small bitmap icon (column-major, LSB=top)."""
        gfx.bitmap_col_major(self._fb, data, x, y, w, h, color)


class Display4Gray:
    """4-grayscale e-paper canvas.

    Provides a ``framebuf.FrameBuffer`` in ``GS2_HMSB`` mode (2 bits per
    pixel) giving four gray levels: white, light gray, dark gray, black.

    Supports both landscape (296×128, default) and portrait (128×296)
    orientations.  Landscape mode rotates the image at refresh time.

    Usage::

        from pico_paper_lib.display import Display4Gray
        from pico_paper_lib.display import GRAY_BLACK, GRAY_DARKGRAY
        from pico_paper_lib.display import GRAY_LIGHTGRAY, GRAY_WHITE

        g = Display4Gray()               # landscape by default
        g.clear()
        g.fill_rect(0, 0, 296, 32, GRAY_BLACK)
        g.text('Hello 4-gray!', 10, 10, GRAY_WHITE)
        g.refresh()

    .. note::
        After using 4-gray mode, call ``reinit_mono()`` to return
        a standard ``Display`` to normal 1-bit operation.
    """

    def __init__(self, orientation=LANDSCAPE, **pin_kwargs):
        self._drv = Driver(**pin_kwargs)
        self._orientation = orientation
        if orientation == LANDSCAPE:
            self.width = HEIGHT   # 296
            self.height = WIDTH   # 128
        else:
            self.width = WIDTH    # 128
            self.height = HEIGHT  # 296
        self._buf = bytearray(HEIGHT * WIDTH // 4)
        self._fb = framebuf.FrameBuffer(
            self._buf, self.width, self.height, framebuf.GS2_HMSB
        )
        self._font = font_small

    @property
    def framebuffer(self):
        """Direct access to the underlying FrameBuffer."""
        return self._fb

    @property
    def buffer(self):
        """Raw byte buffer backing the framebuffer."""
        return self._buf

    # ------------------------------------------------------------------
    # Canvas
    # ------------------------------------------------------------------
    def clear(self, color=GRAY_WHITE):
        """Fill the canvas with a gray level."""
        self._fb.fill(color)

    def fill(self, color):
        """Alias for clear."""
        self._fb.fill(color)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    def refresh(self):
        """Push the 4-gray canvas to the display (full refresh only)."""
        if self._orientation == LANDSCAPE:
            self._drv.gray4_update_landscape(self._buf)
        else:
            self._drv.gray4_update(self._buf)

    def reinit_mono(self):
        """Re-initialise the driver for standard 1-bit mode."""
        self._drv.reinit()

    def sleep(self):
        """Put the e-paper into deep-sleep mode."""
        self._drv.sleep()

    def wake(self):
        """Wake from deep-sleep and re-initialise."""
        self._drv.wake()

    # ------------------------------------------------------------------
    # Drawing (framebuf builtins — colors are 0..3)
    # ------------------------------------------------------------------
    def pixel(self, x, y, color=GRAY_BLACK):
        self._fb.pixel(x, y, color)

    def line(self, x0, y0, x1, y1, color=GRAY_BLACK):
        self._fb.line(x0, y0, x1, y1, color)

    def hline(self, x, y, w, color=GRAY_BLACK):
        self._fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=GRAY_BLACK):
        self._fb.vline(x, y, h, color)

    def rect(self, x, y, w, h, color=GRAY_BLACK, fill=False):
        if fill:
            self._fb.fill_rect(x, y, w, h, color)
        else:
            self._fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=GRAY_BLACK):
        self._fb.fill_rect(x, y, w, h, color)

    def text(self, s, x, y, color=GRAY_BLACK, font=None):
        """Draw text at (x, y) using the current or specified font."""
        f = font or self._font
        f.draw_text(self._fb, s, x, y, color)

    def text_centered(self, s, cx, y, color=GRAY_BLACK, font=None):
        """Draw text horizontally centered around *cx*."""
        f = font or self._font
        f.draw_text_centered(self._fb, s, cx, y, color)

    def text_right(self, s, right_x, y, color=GRAY_BLACK, font=None):
        """Draw text right-aligned at *right_x*."""
        f = font or self._font
        f.draw_text_right(self._fb, s, right_x, y, color)

    def text_width(self, s, font=None):
        """Return pixel width of string *s*."""
        f = font or self._font
        return f.text_width(s)

    def set_font(self, font):
        self._font = font

    def icon(self, data, x, y, w=7, h=7, color=GRAY_BLACK):
        """Draw a column-major bitmap icon (LSB=top)."""
        for col in range(w):
            byte = data[col]
            for row in range(h):
                if byte & (1 << row):
                    self._fb.pixel(x + col, y + row, color)

    def badge(self, s, x, y, color=GRAY_BLACK, padding=2, font=None):
        """Draw a text badge (inverted text in a filled rectangle)."""
        f = font or self._font
        tw = f.text_width(s)
        th = f.CHAR_H
        bw = tw + padding * 2
        bh = th + padding * 2
        self.fill_rect(x, y, bw, bh, color)
        inv = GRAY_WHITE if color <= GRAY_DARKGRAY else GRAY_BLACK
        f.draw_text(self._fb, s, x + padding, y + padding, inv)
