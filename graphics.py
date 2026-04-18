# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jonathan Brenes
"""
Drawing primitives for monochrome frame-buffer displays.

All functions operate on a standard ``framebuf.FrameBuffer`` instance so they
work with any display driver that exposes one.

Coordinates use *landscape* orientation: x 0..295, y 0..127 for the 2.9" panel.
"""

import math


# ------------------------------------------------------------------
# Lines
# ------------------------------------------------------------------
def thick_line(fb, x0, y0, x1, y1, color, thickness=1):
    """Draw a line with adjustable thickness (centered on the path).

    *fb* is a ``framebuf.FrameBuffer``.  If *thickness* is 1 or less,
    delegates to ``fb.line()`` directly.  For a zero-length line
    (start == end), draws a single pixel.
    """
    if thickness <= 1:
        fb.line(x0, y0, x1, y1, color)
        return
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        fb.pixel(x0, y0, color)
        return
    # perpendicular unit vector
    px = -dy / length
    py = dx / length
    half = thickness / 2
    for i in range(thickness):
        off = -half + i + 0.5
        ox = int(px * off)
        oy = int(py * off)
        fb.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)


def dashed_line(fb, x0, y0, x1, y1, color, dash=4, gap=3):
    """Draw a dashed line from (x0,y0) to (x1,y1).

    *dash* and *gap* are pixel lengths for drawn and skipped segments.
    """
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        fb.pixel(x0, y0, color)
        return
    ux = dx / length
    uy = dy / length
    d = 0.0
    drawing = True
    seg = dash
    while d < length:
        seg_len = min(seg, length - d)
        sx = int(x0 + ux * d)
        sy = int(y0 + uy * d)
        ex = int(x0 + ux * (d + seg_len))
        ey = int(y0 + uy * (d + seg_len))
        if drawing:
            fb.line(sx, sy, ex, ey, color)
        d += seg_len
        drawing = not drawing
        seg = gap if drawing else dash


def dotted_line(fb, x0, y0, x1, y1, color, spacing=3):
    """Draw a dotted line (individual pixels at *spacing* intervals)."""
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        fb.pixel(x0, y0, color)
        return
    ux = dx / length
    uy = dy / length
    d = 0.0
    while d <= length:
        fb.pixel(int(x0 + ux * d), int(y0 + uy * d), color)
        d += spacing


# ------------------------------------------------------------------
# Rectangles
# ------------------------------------------------------------------
def rect(fb, x, y, w, h, color, fill=False):
    """Draw a rectangle — filled or outline only."""
    if fill:
        fb.fill_rect(x, y, w, h, color)
    else:
        fb.rect(x, y, w, h, color)


def rounded_rect(fb, x, y, w, h, r, color, fill=False):
    """Draw a rectangle with rounded corners of radius *r*."""
    r = min(r, w // 2, h // 2)
    if fill:
        fb.fill_rect(x + r, y, w - 2 * r, h, color)
        fb.fill_rect(x, y + r, w, h - 2 * r, color)
        _fill_circle_helper(fb, x + r, y + r, r, color, 1)
        _fill_circle_helper(fb, x + w - r - 1, y + r, r, color, 2)
        _fill_circle_helper(fb, x + r, y + h - r - 1, r, color, 4)
        _fill_circle_helper(fb, x + w - r - 1, y + h - r - 1, r, color, 8)
    else:
        fb.hline(x + r, y, w - 2 * r, color)
        fb.hline(x + r, y + h - 1, w - 2 * r, color)
        fb.vline(x, y + r, h - 2 * r, color)
        fb.vline(x + w - 1, y + r, h - 2 * r, color)
        _arc_quarter(fb, x + r, y + r, r, color, 1)
        _arc_quarter(fb, x + w - r - 1, y + r, r, color, 2)
        _arc_quarter(fb, x + r, y + h - r - 1, r, color, 4)
        _arc_quarter(fb, x + w - r - 1, y + h - r - 1, r, color, 8)


# ------------------------------------------------------------------
# Circles & ellipses
# ------------------------------------------------------------------
def circle(fb, cx, cy, r, color, fill=False):
    """Draw a circle using the midpoint algorithm."""
    if fill:
        _fill_circle(fb, cx, cy, r, color)
    else:
        _stroke_circle(fb, cx, cy, r, color)


def _stroke_circle(fb, cx, cy, r, c):
    """Draw a circle outline using the midpoint (Bresenham) algorithm."""
    x = r
    y = 0
    err = -r
    while x >= y:
        fb.pixel(cx + x, cy + y, c)
        fb.pixel(cx + y, cy + x, c)
        fb.pixel(cx - y, cy + x, c)
        fb.pixel(cx - x, cy + y, c)
        fb.pixel(cx - x, cy - y, c)
        fb.pixel(cx - y, cy - x, c)
        fb.pixel(cx + y, cy - x, c)
        fb.pixel(cx + x, cy - y, c)
        y += 1
        err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def _fill_circle(fb, cx, cy, r, c):
    """Draw a filled circle using horizontal scanlines (midpoint algorithm)."""
    x = r
    y = 0
    err = -r
    while x >= y:
        fb.hline(cx - x, cy + y, 2 * x + 1, c)
        fb.hline(cx - y, cy + x, 2 * y + 1, c)
        fb.hline(cx - x, cy - y, 2 * x + 1, c)
        fb.hline(cx - y, cy - x, 2 * y + 1, c)
        y += 1
        err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def _arc_quarter(fb, cx, cy, r, c, corner):
    """Draw one quarter-arc.  corner: 1=TL, 2=TR, 4=BL, 8=BR."""
    x = r
    y = 0
    err = -r
    while x >= y:
        if corner & 1:   # top-left
            fb.pixel(cx - x, cy - y, c)
            fb.pixel(cx - y, cy - x, c)
        if corner & 2:   # top-right
            fb.pixel(cx + x, cy - y, c)
            fb.pixel(cx + y, cy - x, c)
        if corner & 4:   # bottom-left
            fb.pixel(cx - x, cy + y, c)
            fb.pixel(cx - y, cy + x, c)
        if corner & 8:   # bottom-right
            fb.pixel(cx + x, cy + y, c)
            fb.pixel(cx + y, cy + x, c)
        y += 1
        err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def _fill_circle_helper(fb, cx, cy, r, c, corner):
    """Fill one quarter of a circle. corner: 1=TL, 2=TR, 4=BL, 8=BR."""
    x = r
    y = 0
    err = -r
    while x >= y:
        if corner & 1:
            fb.hline(cx - x, cy - y, x + 1, c)
            fb.hline(cx - y, cy - x, y + 1, c)
        if corner & 2:
            fb.hline(cx, cy - y, x + 1, c)
            fb.hline(cx, cy - x, y + 1, c)
        if corner & 4:
            fb.hline(cx - x, cy + y, x + 1, c)
            fb.hline(cx - y, cy + x, y + 1, c)
        if corner & 8:
            fb.hline(cx, cy + y, x + 1, c)
            fb.hline(cx, cy + x, y + 1, c)
        y += 1
        err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def ellipse(fb, cx, cy, rx, ry, color, fill=False):
    """Draw an ellipse (Bresenham, integer-only)."""
    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    err = ry2 - rx2 * ry + rx2 // 4
    while ry2 * x <= rx2 * y:
        if fill:
            fb.hline(cx - x, cy + y, 2 * x + 1, color)
            fb.hline(cx - x, cy - y, 2 * x + 1, color)
        else:
            fb.pixel(cx + x, cy + y, color)
            fb.pixel(cx - x, cy + y, color)
            fb.pixel(cx + x, cy - y, color)
            fb.pixel(cx - x, cy - y, color)
        x += 1
        if err < 0:
            err += ry2 * (2 * x + 1)
        else:
            y -= 1
            err += ry2 * (2 * x + 1) - 2 * rx2 * y
    err2 = ry2 * (x * x + x) + rx2 * (y - 1) * (y - 1) - rx2 * ry2
    while y >= 0:
        if fill:
            fb.hline(cx - x, cy + y, 2 * x + 1, color)
            fb.hline(cx - x, cy - y, 2 * x + 1, color)
        else:
            fb.pixel(cx + x, cy + y, color)
            fb.pixel(cx - x, cy + y, color)
            fb.pixel(cx + x, cy - y, color)
            fb.pixel(cx - x, cy - y, color)
        y -= 1
        if err2 > 0:
            err2 -= rx2 * (2 * y + 1)
        else:
            x += 1
            err2 += ry2 * (2 * x + 1) - rx2 * (2 * y + 1)


# ------------------------------------------------------------------
# Triangles & polygons
# ------------------------------------------------------------------
def triangle(fb, x0, y0, x1, y1, x2, y2, color, fill=False):
    """Draw a triangle (outline or scanline-filled)."""
    if fill:
        _fill_triangle(fb, x0, y0, x1, y1, x2, y2, color)
    else:
        fb.line(x0, y0, x1, y1, color)
        fb.line(x1, y1, x2, y2, color)
        fb.line(x2, y2, x0, y0, color)


def _fill_triangle(fb, x0, y0, x1, y1, x2, y2, c):
    """Scanline-fill a triangle. Vertices are sorted by Y, then each row is interpolated."""
    # Sort vertices by y
    if y0 > y1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    if y0 > y2:
        x0, y0, x2, y2 = x2, y2, x0, y0
    if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1
    if y0 == y2:
        a = b = x0
        a = min(a, x1, x2)
        b = max(b, x1, x2)
        fb.hline(a, y0, b - a + 1, c)
        return
    for y in range(y0, y2 + 1):
        if y < y1:
            xa = x0 + (x1 - x0) * (y - y0) // (y1 - y0) if y1 != y0 else x0
        else:
            xa = x1 + (x2 - x1) * (y - y1) // (y2 - y1) if y2 != y1 else x1
        xb = x0 + (x2 - x0) * (y - y0) // (y2 - y0)
        if xa > xb:
            xa, xb = xb, xa
        fb.hline(xa, y, xb - xa + 1, c)


def polygon(fb, points, color, fill=False):
    """Draw a polygon from a list of (x, y) tuples.

    Outline uses line segments; fill uses horizontal scanline.
    """
    n = len(points)
    if n < 3:
        return
    if fill:
        _fill_polygon(fb, points, color)
    else:
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            fb.line(x0, y0, x1, y1, color)


def _fill_polygon(fb, pts, c):
    """Scanline fill for convex or simple concave polygons."""
    n = len(pts)
    ymin = min(p[1] for p in pts)
    ymax = max(p[1] for p in pts)
    for y in range(ymin, ymax + 1):
        nodes = []
        j = n - 1
        for i in range(n):
            yi = pts[i][1]
            yj = pts[j][1]
            if (yi < y <= yj) or (yj < y <= yi):
                xi = pts[i][0]
                xj = pts[j][0]
                x = xi + (y - yi) * (xj - xi) // (yj - yi)
                nodes.append(x)
            j = i
        nodes.sort()
        for k in range(0, len(nodes) - 1, 2):
            fb.hline(nodes[k], y, nodes[k + 1] - nodes[k] + 1, c)


# ------------------------------------------------------------------
# Bitmap / icon helpers
# ------------------------------------------------------------------
def bitmap_col_major(fb, data, x, y, w, h, color):
    """Draw a column-major bitmap (1 bit per pixel, LSB = top row).

    Each byte in *data* represents one column of up to 8 pixels.
    Bit 0 is the top pixel, bit 7 is the bottom.  *data* length
    must be >= *w*.  Only set bits are drawn (transparent background).
    """
    for col in range(w):
        byte = data[col]
        for row in range(h):
            if byte & (1 << row):
                fb.pixel(x + col, y + row, color)


def bitmap_row_major(fb, data, x, y, w, h, color):
    """Draw a row-major bitmap (MSB-first, padded to byte boundary per row).

    Each row is ceil(w/8) bytes wide.  Bit 7 of each byte is the leftmost
    pixel.  Only set bits are drawn (transparent background).
    """
    bw = (w + 7) // 8
    for row in range(h):
        for col in range(w):
            byte_idx = row * bw + col // 8
            bit_idx = 7 - (col % 8)
            if data[byte_idx] & (1 << bit_idx):
                fb.pixel(x + col, y + row, color)


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------
def flood_fill(fb, x, y, fill_color, w, h, bg_color=0xFF):
    """Simple stack-based flood fill bounded by *w* x *h*.

    Fills contiguous pixels matching *bg_color* starting from (x, y).

    WARNING: uses a Python list as a stack — can consume significant RAM
    on large areas.  Best for small enclosed regions (< 1000 pixels).
    For large fills, prefer ``fill_rect()`` or scanline approaches.
    """
    if fb.pixel(x, y) != bg_color:
        return
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if fb.pixel(cx, cy) != bg_color:
            continue
        fb.pixel(cx, cy, fill_color)
        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))
