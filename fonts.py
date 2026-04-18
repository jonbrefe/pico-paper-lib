"""
Font base class and built-in bitmap fonts for e-paper text rendering.
"""

from micropython import const


class BitmapFont:
    """Base class for column-major bitmap fonts.

    Subclasses must set ``_DATA``, ``_FIRST``, ``_LAST``, ``CHAR_W``, and
    ``CHAR_H``.  Each character is stored as *CHAR_W* bytes, one per column,
    with LSB = top row.
    """

    _DATA = b''
    _EXT = {}     # {codepoint: bytes} for characters outside _FIRST.._LAST
    _FIRST = 32   # first ASCII code in the font table
    _LAST = 126   # last ASCII code in the font table
    CHAR_W = 5    # pixel width of each glyph
    CHAR_H = 7    # pixel height of each glyph
    GAP = 1       # inter-character gap in pixels

    @property
    def cell_w(self):
        return self.CHAR_W + self.GAP

    def _glyph(self, ch):
        """Return (data, offset) for a character.

        Checks the main ASCII table first, then the _EXT dict for
        accented / special characters, falling back to '?'.
        """
        code = ord(ch)
        if self._FIRST <= code <= self._LAST:
            return (self._DATA, (code - self._FIRST) * self.CHAR_W)
        g = self._EXT.get(code)
        if g:
            return (g, 0)
        return (self._DATA, (ord('?') - self._FIRST) * self.CHAR_W)

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------
    def text_width(self, s):
        """Return the pixel width of string *s*."""
        n = len(s)
        return n * self.cell_w - self.GAP if n else 0

    def text_height(self):
        """Return the pixel height of a single line of text."""
        return self.CHAR_H

    def wrap_lines(self, s, max_width):
        """Word-wrap *s* to fit within *max_width* pixels.

        Returns a list of strings (one per line).
        """
        words = s.split(' ')
        lines = []
        line = ''
        for word in words:
            test = (line + ' ' + word).strip()
            if self.text_width(test) > max_width:
                if line:
                    lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)
        return lines

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_char(self, fb, ch, x, y, color):
        """Draw a single character on *fb* and return advance width."""
        data, off = self._glyph(ch)
        for col in range(self.CHAR_W):
            byte = data[off + col]
            for row in range(8):
                if byte & (1 << row):
                    fb.pixel(x + col, y + row, color)
        return self.cell_w

    def draw_text(self, fb, s, x, y, color):
        """Draw a string left-aligned at (x, y)."""
        cx = x
        for ch in s:
            cx += self.draw_char(fb, ch, cx, y, color)
        return cx - x  # total width drawn

    def draw_text_centered(self, fb, s, cx, y, color):
        """Draw *s* horizontally centered around *cx*."""
        w = self.text_width(s)
        self.draw_text(fb, s, cx - w // 2, y, color)

    def draw_text_right(self, fb, s, right_x, y, color):
        """Draw *s* right-aligned so its last pixel is at *right_x*."""
        w = self.text_width(s)
        self.draw_text(fb, s, right_x - w, y, color)

    def draw_text_in_rect(self, fb, s, x, y, w, h, color,
                          align='left', valign='top', wrap=False, pad=4):
        """Draw text inside a bounding box with alignment and optional wrap.

        align:  'left' | 'center' | 'right'
        valign: 'top'  | 'middle' | 'bottom'
        pad:    pixel padding inside the rectangle edges (default 4)
        """
        ix, iy, iw, ih = x + pad, y + pad, w - 2 * pad, h - 2 * pad
        if wrap:
            lines = self.wrap_lines(s, iw)
        else:
            lines = [s]
        total_h = len(lines) * (self.CHAR_H + 1) - 1
        if valign == 'middle':
            ty = iy + (ih - total_h) // 2
        elif valign == 'bottom':
            ty = iy + ih - total_h
        else:
            ty = iy
        for line in lines:
            lw = self.text_width(line)
            if align == 'center':
                tx = ix + (iw - lw) // 2
            elif align == 'right':
                tx = ix + iw - lw
            else:
                tx = ix
            self.draw_text(fb, line, tx, ty, color)
            ty += self.CHAR_H + 1

    def draw_text_wrapped(self, fb, s, x, y, max_width, color, line_spacing=1):
        """Draw word-wrapped text starting at (x, y).

        Returns total height used.
        """
        lines = self.wrap_lines(s, max_width)
        cy = y
        for line in lines:
            self.draw_text(fb, line, x, cy, color)
            cy += self.CHAR_H + line_spacing
        return cy - y


# ======================================================================
# Built-in 5x7 font (ASCII 32-126)
# ======================================================================
class Font5x7(BitmapFont):
    """Compact 5x7 bitmap font — the default for small e-paper displays."""

    CHAR_W = 5
    CHAR_H = 7
    GAP = 1
    _FIRST = 32
    _LAST = 126

    _DATA = (
        b'\x00\x00\x00\x00\x00'  # 32 space
        b'\x00\x00\x5f\x00\x00'  # 33 !
        b'\x00\x07\x00\x07\x00'  # 34 "
        b'\x14\x7f\x14\x7f\x14'  # 35 #
        b'\x24\x2a\x7f\x2a\x12'  # 36 $
        b'\x23\x13\x08\x64\x62'  # 37 %
        b'\x36\x49\x55\x22\x50'  # 38 &
        b'\x00\x00\x07\x00\x00'  # 39 '
        b'\x00\x1c\x22\x41\x00'  # 40 (
        b'\x00\x41\x22\x1c\x00'  # 41 )
        b'\x14\x08\x3e\x08\x14'  # 42 *
        b'\x08\x08\x3e\x08\x08'  # 43 +
        b'\x00\x50\x30\x00\x00'  # 44 ,
        b'\x08\x08\x08\x08\x08'  # 45 -
        b'\x00\x60\x60\x00\x00'  # 46 .
        b'\x20\x10\x08\x04\x02'  # 47 /
        b'\x3e\x51\x49\x45\x3e'  # 48 0
        b'\x00\x42\x7f\x40\x00'  # 49 1
        b'\x42\x61\x51\x49\x46'  # 50 2
        b'\x21\x41\x45\x4b\x31'  # 51 3
        b'\x18\x14\x12\x7f\x10'  # 52 4
        b'\x27\x45\x45\x45\x39'  # 53 5
        b'\x3c\x4a\x49\x49\x30'  # 54 6
        b'\x01\x71\x09\x05\x03'  # 55 7
        b'\x36\x49\x49\x49\x36'  # 56 8
        b'\x06\x49\x49\x29\x1e'  # 57 9
        b'\x00\x36\x36\x00\x00'  # 58 :
        b'\x00\x56\x36\x00\x00'  # 59 ;
        b'\x08\x14\x22\x41\x00'  # 60 <
        b'\x14\x14\x14\x14\x14'  # 61 =
        b'\x00\x41\x22\x14\x08'  # 62 >
        b'\x02\x01\x51\x09\x06'  # 63 ?
        b'\x3e\x41\x5d\x55\x1e'  # 64 @
        b'\x7e\x09\x09\x09\x7e'  # 65 A
        b'\x7f\x49\x49\x49\x36'  # 66 B
        b'\x3e\x41\x41\x41\x22'  # 67 C
        b'\x7f\x41\x41\x22\x1c'  # 68 D
        b'\x7f\x49\x49\x49\x41'  # 69 E
        b'\x7f\x09\x09\x09\x01'  # 70 F
        b'\x3e\x41\x49\x49\x3a'  # 71 G
        b'\x7f\x08\x08\x08\x7f'  # 72 H
        b'\x00\x41\x7f\x41\x00'  # 73 I
        b'\x20\x40\x41\x3f\x01'  # 74 J
        b'\x7f\x08\x14\x22\x41'  # 75 K
        b'\x7f\x40\x40\x40\x40'  # 76 L
        b'\x7f\x02\x0c\x02\x7f'  # 77 M
        b'\x7f\x04\x08\x10\x7f'  # 78 N
        b'\x3e\x41\x41\x41\x3e'  # 79 O
        b'\x7f\x09\x09\x09\x06'  # 80 P
        b'\x3e\x41\x51\x21\x5e'  # 81 Q
        b'\x7f\x09\x19\x29\x46'  # 82 R
        b'\x46\x49\x49\x49\x31'  # 83 S
        b'\x01\x01\x7f\x01\x01'  # 84 T
        b'\x3f\x40\x40\x40\x3f'  # 85 U
        b'\x1f\x20\x40\x20\x1f'  # 86 V
        b'\x3f\x40\x30\x40\x3f'  # 87 W
        b'\x63\x14\x08\x14\x63'  # 88 X
        b'\x07\x08\x70\x08\x07'  # 89 Y
        b'\x61\x51\x49\x45\x43'  # 90 Z
        b'\x00\x7f\x41\x41\x00'  # 91 [
        b'\x02\x04\x08\x10\x20'  # 92 backslash
        b'\x00\x41\x41\x7f\x00'  # 93 ]
        b'\x04\x02\x01\x02\x04'  # 94 ^
        b'\x40\x40\x40\x40\x40'  # 95 _
        b'\x00\x01\x02\x04\x00'  # 96 `
        b'\x20\x54\x54\x54\x78'  # 97 a
        b'\x7f\x44\x44\x44\x38'  # 98 b
        b'\x38\x44\x44\x44\x20'  # 99 c
        b'\x38\x44\x44\x44\x7f'  # 100 d
        b'\x38\x54\x54\x54\x18'  # 101 e
        b'\x08\x7e\x09\x01\x02'  # 102 f
        b'\x18\xa4\xa4\xa4\x7c'  # 103 g
        b'\x7f\x04\x04\x04\x78'  # 104 h
        b'\x00\x44\x7d\x40\x00'  # 105 i
        b'\x40\x80\x84\x7d\x00'  # 106 j
        b'\x7f\x10\x28\x44\x00'  # 107 k
        b'\x00\x41\x7f\x40\x00'  # 108 l
        b'\x7c\x04\x18\x04\x78'  # 109 m
        b'\x7c\x08\x04\x04\x78'  # 110 n
        b'\x38\x44\x44\x44\x38'  # 111 o
        b'\xfc\x24\x24\x24\x18'  # 112 p
        b'\x18\x24\x24\x24\xfc'  # 113 q
        b'\x7c\x08\x04\x04\x08'  # 114 r
        b'\x48\x54\x54\x54\x20'  # 115 s
        b'\x04\x3f\x44\x40\x20'  # 116 t
        b'\x3c\x40\x40\x20\x7c'  # 117 u
        b'\x1c\x20\x40\x20\x1c'  # 118 v
        b'\x3c\x40\x30\x40\x3c'  # 119 w
        b'\x44\x28\x10\x28\x44'  # 120 x
        b'\x1c\xa0\xa0\xa0\x7c'  # 121 y
        b'\x44\x64\x54\x4c\x44'  # 122 z
        b'\x00\x08\x36\x41\x00'  # 123 {
        b'\x00\x00\x7f\x00\x00'  # 124 |
        b'\x00\x41\x36\x08\x00'  # 125 }
        b'\x08\x04\x08\x10\x08'  # 126 ~
    )

    _EXT = {
        0xA1: b'\x00\x00\x7d\x00\x00',  # ¡
        0xBF: b'\x30\x48\x45\x40\x20',  # ¿
        0xC1: b'\xfc\x12\x12\x13\xfc',  # Á (A shifted+acute)
        0xC9: b'\xfe\x92\x92\x93\x82',  # É (E shifted+acute)
        0xCD: b'\x00\x82\xfe\x83\x00',  # Í (I shifted+acute)
        0xD1: b'\xfe\x09\x10\x21\xfe',  # Ñ (N shifted+tilde)
        0xD3: b'\x7c\x82\x82\x83\x7c',  # Ó (O shifted+acute)
        0xDA: b'\x7e\x80\x80\x81\x7e',  # Ú (U shifted+acute)
        0xDC: b'\x7e\x81\x80\x81\x7e',  # Ü (U shifted+diaeresis)
        0xE1: b'\x20\x54\x56\x55\x78',  # á (a+acute)
        0xE9: b'\x38\x54\x56\x55\x18',  # é (e+acute)
        0xED: b'\x00\x44\x7c\x41\x00',  # í (i dot→acute)
        0xF1: b'\x7c\x09\x04\x05\x78',  # ñ (n+tilde)
        0xF3: b'\x38\x44\x46\x45\x38',  # ó (o+acute)
        0xFA: b'\x3c\x40\x42\x21\x7c',  # ú (u+acute)
        0xFC: b'\x3c\x41\x40\x21\x7c',  # ü (u+diaeresis)
    }


# ======================================================================
# Built-in 8x8 bold font (ASCII 32-126)
# ======================================================================
class Font8x8(BitmapFont):
    """8x8 bitmap font — more readable on larger displays or headers."""

    CHAR_W = 8
    CHAR_H = 8
    GAP = 1
    _FIRST = 32
    _LAST = 126

    # Column-major, LSB = top row.  Standard CP437-style 8x8 glyphs.
    _DATA = (
        b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 32 space
        b'\x00\x00\x06\x5f\x5f\x06\x00\x00'  # 33 !
        b'\x00\x03\x07\x00\x03\x07\x00\x00'  # 34 "
        b'\x14\x7f\x7f\x14\x7f\x7f\x14\x00'  # 35 #
        b'\x24\x2e\x6b\x6b\x3a\x12\x00\x00'  # 36 $
        b'\x46\x66\x30\x18\x0c\x66\x62\x00'  # 37 %
        b'\x30\x7a\x4f\x5d\x37\x7a\x48\x00'  # 38 &
        b'\x00\x04\x07\x03\x00\x00\x00\x00'  # 39 '
        b'\x00\x1c\x3e\x63\x41\x00\x00\x00'  # 40 (
        b'\x00\x41\x63\x3e\x1c\x00\x00\x00'  # 41 )
        b'\x08\x2a\x3e\x1c\x1c\x3e\x2a\x08'  # 42 *
        b'\x08\x08\x3e\x3e\x08\x08\x00\x00'  # 43 +
        b'\x00\x80\xe0\x60\x00\x00\x00\x00'  # 44 ,
        b'\x08\x08\x08\x08\x08\x08\x00\x00'  # 45 -
        b'\x00\x00\x60\x60\x00\x00\x00\x00'  # 46 .
        b'\x60\x30\x18\x0c\x06\x03\x01\x00'  # 47 /
        b'\x3e\x7f\x51\x49\x45\x7f\x3e\x00'  # 48 0
        b'\x40\x42\x7f\x7f\x40\x40\x00\x00'  # 49 1
        b'\x62\x73\x59\x49\x6f\x66\x00\x00'  # 50 2
        b'\x22\x63\x49\x49\x7f\x36\x00\x00'  # 51 3
        b'\x18\x1c\x16\x13\x7f\x7f\x10\x00'  # 52 4
        b'\x27\x67\x45\x45\x7d\x39\x00\x00'  # 53 5
        b'\x3c\x7e\x4b\x49\x79\x30\x00\x00'  # 54 6
        b'\x03\x03\x71\x79\x0f\x07\x00\x00'  # 55 7
        b'\x36\x7f\x49\x49\x7f\x36\x00\x00'  # 56 8
        b'\x06\x4f\x49\x69\x3f\x1e\x00\x00'  # 57 9
        b'\x00\x00\x36\x36\x00\x00\x00\x00'  # 58 :
        b'\x00\x80\xb6\x36\x00\x00\x00\x00'  # 59 ;
        b'\x08\x1c\x36\x63\x41\x00\x00\x00'  # 60 <
        b'\x14\x14\x14\x14\x14\x14\x00\x00'  # 61 =
        b'\x00\x41\x63\x36\x1c\x08\x00\x00'  # 62 >
        b'\x02\x03\x51\x59\x0f\x06\x00\x00'  # 63 ?
        b'\x3e\x7f\x41\x5d\x55\x1f\x1e\x00'  # 64 @
        b'\x7c\x7e\x13\x11\x13\x7e\x7c\x00'  # 65 A
        b'\x41\x7f\x7f\x49\x49\x7f\x36\x00'  # 66 B
        b'\x1c\x3e\x63\x41\x41\x63\x22\x00'  # 67 C
        b'\x41\x7f\x7f\x41\x63\x3e\x1c\x00'  # 68 D
        b'\x41\x7f\x7f\x49\x5d\x41\x63\x00'  # 69 E
        b'\x41\x7f\x7f\x49\x1d\x01\x03\x00'  # 70 F
        b'\x1c\x3e\x63\x41\x51\x73\x72\x00'  # 71 G
        b'\x7f\x7f\x08\x08\x7f\x7f\x00\x00'  # 72 H
        b'\x00\x41\x7f\x7f\x41\x00\x00\x00'  # 73 I
        b'\x30\x70\x40\x41\x7f\x3f\x01\x00'  # 74 J
        b'\x41\x7f\x7f\x08\x1c\x77\x63\x00'  # 75 K
        b'\x41\x7f\x7f\x41\x40\x60\x70\x00'  # 76 L
        b'\x7f\x7f\x0e\x1c\x0e\x7f\x7f\x00'  # 77 M
        b'\x7f\x7f\x06\x0c\x18\x7f\x7f\x00'  # 78 N
        b'\x1c\x3e\x63\x41\x63\x3e\x1c\x00'  # 79 O
        b'\x41\x7f\x7f\x49\x09\x0f\x06\x00'  # 80 P
        b'\x1e\x3f\x21\x71\x7f\x5e\x00\x00'  # 81 Q
        b'\x41\x7f\x7f\x09\x19\x7f\x66\x00'  # 82 R
        b'\x26\x6f\x4d\x59\x73\x32\x00\x00'  # 83 S
        b'\x03\x41\x7f\x7f\x41\x03\x00\x00'  # 84 T
        b'\x7f\x7f\x40\x40\x7f\x7f\x00\x00'  # 85 U
        b'\x1f\x3f\x60\x60\x3f\x1f\x00\x00'  # 86 V
        b'\x7f\x7f\x30\x18\x30\x7f\x7f\x00'  # 87 W
        b'\x43\x67\x3c\x18\x3c\x67\x43\x00'  # 88 X
        b'\x07\x4f\x78\x78\x4f\x07\x00\x00'  # 89 Y
        b'\x47\x63\x71\x59\x4d\x67\x73\x00'  # 90 Z
        b'\x00\x7f\x7f\x41\x41\x00\x00\x00'  # 91 [
        b'\x01\x03\x06\x0c\x18\x30\x60\x00'  # 92 backslash
        b'\x00\x41\x41\x7f\x7f\x00\x00\x00'  # 93 ]
        b'\x08\x0c\x06\x03\x06\x0c\x08\x00'  # 94 ^
        b'\x80\x80\x80\x80\x80\x80\x80\x80'  # 95 _
        b'\x00\x00\x03\x07\x04\x00\x00\x00'  # 96 `
        b'\x20\x74\x54\x54\x3c\x78\x40\x00'  # 97 a
        b'\x41\x7f\x3f\x44\x44\x7c\x38\x00'  # 98 b
        b'\x38\x7c\x44\x44\x6c\x28\x00\x00'  # 99 c
        b'\x38\x7c\x44\x45\x3f\x7f\x40\x00'  # 100 d
        b'\x38\x7c\x54\x54\x5c\x18\x00\x00'  # 101 e
        b'\x48\x7e\x7f\x49\x03\x02\x00\x00'  # 102 f
        b'\x98\xbc\xa4\xa4\xf8\x7c\x04\x00'  # 103 g
        b'\x41\x7f\x7f\x08\x04\x7c\x78\x00'  # 104 h
        b'\x00\x44\x7d\x7d\x40\x00\x00\x00'  # 105 i
        b'\x60\xe0\x80\x80\xfd\x7d\x00\x00'  # 106 j
        b'\x41\x7f\x7f\x10\x38\x6c\x44\x00'  # 107 k
        b'\x00\x41\x7f\x7f\x40\x00\x00\x00'  # 108 l
        b'\x7c\x7c\x18\x38\x1c\x7c\x78\x00'  # 109 m
        b'\x7c\x7c\x08\x04\x04\x7c\x78\x00'  # 110 n
        b'\x38\x7c\x44\x44\x7c\x38\x00\x00'  # 111 o
        b'\x84\xfc\xf8\xa4\x24\x3c\x18\x00'  # 112 p
        b'\x18\x3c\x24\xa4\xf8\xfc\x84\x00'  # 113 q
        b'\x44\x7c\x78\x4c\x04\x1c\x18\x00'  # 114 r
        b'\x48\x5c\x54\x54\x74\x24\x00\x00'  # 115 s
        b'\x00\x04\x3e\x7f\x44\x24\x00\x00'  # 116 t
        b'\x3c\x7c\x40\x40\x3c\x7c\x40\x00'  # 117 u
        b'\x1c\x3c\x60\x60\x3c\x1c\x00\x00'  # 118 v
        b'\x3c\x7c\x70\x38\x70\x7c\x3c\x00'  # 119 w
        b'\x44\x6c\x38\x10\x38\x6c\x44\x00'  # 120 x
        b'\x9c\xbc\xa0\xa0\xfc\x7c\x00\x00'  # 121 y
        b'\x4c\x64\x74\x5c\x4c\x64\x00\x00'  # 122 z
        b'\x08\x08\x3e\x77\x41\x41\x00\x00'  # 123 {
        b'\x00\x00\x00\x77\x77\x00\x00\x00'  # 124 |
        b'\x41\x41\x77\x3e\x08\x08\x00\x00'  # 125 }
        b'\x02\x03\x01\x03\x02\x03\x01\x00'  # 126 ~
    )

    _EXT = {
        0xA1: b'\x00\x00\x30\x7d\x7d\x30\x00\x00',  # ¡
        0xBF: b'\x20\x60\x45\x4d\x78\x30\x00\x00',  # ¿
        0xC1: b'\xf8\xfc\x26\x22\x27\xfc\xf8\x00',  # Á
        0xC9: b'\x82\xfe\xfe\x92\xbb\x82\xc6\x00',  # É
        0xCD: b'\x00\x82\xfe\xff\x82\x00\x00\x00',  # Í
        0xD1: b'\xfe\xfe\x0d\x18\x31\xfe\xfe\x00',  # Ñ
        0xD3: b'\x38\x7c\xc6\x82\xc7\x7c\x38\x00',  # Ó
        0xDA: b'\xfe\xfe\x80\x81\xfe\xfe\x00\x00',  # Ú
        0xDC: b'\xfe\xff\x80\x80\xff\xfe\x00\x00',  # Ü
        0xE1: b'\x20\x74\x54\x56\x3d\x78\x40\x00',  # á
        0xE9: b'\x38\x7c\x54\x56\x5d\x18\x00\x00',  # é
        0xED: b'\x00\x44\x7c\x7e\x41\x00\x00\x00',  # í
        0xF1: b'\x7c\x7c\x09\x04\x05\x7c\x78\x00',  # ñ
        0xF3: b'\x38\x7c\x44\x46\x7d\x38\x00\x00',  # ó
        0xFA: b'\x3c\x7c\x40\x42\x3d\x7c\x40\x00',  # ú
        0xFC: b'\x3c\x7d\x40\x40\x3d\x7c\x40\x00',  # ü
    }


# Pre-instantiated singletons for convenience
font_small = Font5x7()
font_medium = Font8x8()
