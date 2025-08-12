#!/usr/bin/env python3

import math
import struct
from typing import List, Tuple

# Basic RGBA color helpers
Color = Tuple[int, int, int, int]  # (R, G, B, A)

WHITE: Color = (255, 255, 255, 255)
TRANSPARENT: Color = (0, 0, 0, 0)
DARK_GRAY: Color = (120, 120, 120, 255)
LIGHT_GRAY: Color = (210, 210, 210, 255)
EXCEL_GREEN: Color = (16, 124, 16, 255)
DEEP_GREEN: Color = (10, 100, 10, 255)


def create_canvas(width: int, height: int, color: Color = TRANSPARENT) -> List[List[Color]]:
    return [[color for _ in range(width)] for _ in range(height)]


def clamp(x: int, lo: int, hi: int) -> int:
    return lo if x < lo else hi if x > hi else x


def set_pixel(canvas: List[List[Color]], x: int, y: int, color: Color) -> None:
    h = len(canvas)
    w = len(canvas[0]) if h > 0 else 0
    if 0 <= x < w and 0 <= y < h:
        canvas[y][x] = color


def draw_rect(canvas: List[List[Color]], x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
    for y in range(y0, y1 + 1):
        set_pixel(canvas, x0, y, color)
        set_pixel(canvas, x1, y, color)
    for x in range(x0, x1 + 1):
        set_pixel(canvas, x, y0, color)
        set_pixel(canvas, x, y1, color)


def fill_rect(canvas: List[List[Color]], x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            set_pixel(canvas, x, y, color)


def draw_line(canvas: List[List[Color]], x0: int, y0: int, x1: int, y1: int, color: Color) -> None:
    # Bresenham's algorithm
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_pixel(canvas, x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def draw_circle_arc(canvas: List[List[Color]], cx: int, cy: int, radius: int, start_deg: float, end_deg: float, stroke: int, color: Color) -> None:
    # Draw arc by sampling angles; stroke via radial thickness
    steps = max(60, int(radius * 6))
    start_rad = math.radians(start_deg)
    end_rad = math.radians(end_deg)
    # Normalize to ensure correct direction
    if end_rad < start_rad:
        end_rad += 2 * math.pi
    for i in range(steps + 1):
        t = start_rad + (end_rad - start_rad) * (i / steps)
        x = cx + int(round(math.cos(t) * radius))
        y = cy + int(round(math.sin(t) * radius))
        for s in range(-stroke // 2, stroke - stroke // 2):
            xr = cx + int(round(math.cos(t) * (radius + s)))
            yr = cy + int(round(math.sin(t) * (radius + s)))
            set_pixel(canvas, xr, yr, color)


def draw_filled_triangle(canvas: List[List[Color]], p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], color: Color) -> None:
    # Sort points by y
    (x0, y0), (x1, y1), (x2, y2) = sorted([p0, p1, p2], key=lambda p: p[1])
    def edge_interpolate(y, xa, ya, xb, yb):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    # Fill bottom-flat and top-flat triangles
    def fill_flat_bottom(x0, y0, x1, y1, x2, y2):
        invslope1 = (x1 - x0) / (y1 - y0) if y1 != y0 else 0
        invslope2 = (x2 - x0) / (y2 - y0) if y2 != y0 else 0
        curx1 = x0
        curx2 = x0
        for y in range(y0, y1 + 1):
            for x in range(int(math.floor(curx1)), int(math.ceil(curx2)) + 1):
                set_pixel(canvas, x, y, color)
            curx1 += invslope1
            curx2 += invslope2
    def fill_flat_top(x0, y0, x1, y1, x2, y2):
        invslope1 = (x2 - x0) / (y2 - y0) if y2 != y0 else 0
        invslope2 = (x2 - x1) / (y2 - y1) if y2 != y1 else 0
        curx1 = x2
        curx2 = x2
        for y in range(y2, y0 - 1, -1):
            for x in range(int(math.floor(curx1)), int(math.ceil(curx2)) + 1):
                set_pixel(canvas, x, y, color)
            curx1 -= invslope1
            curx2 -= invslope2
    if y1 == y0:
        fill_flat_top(x0, y0, x1, y1, x2, y2)
    elif y1 == y2:
        fill_flat_bottom(x0, y0, x1, y1, x2, y2)
    else:
        x3 = int(round(edge_interpolate(y1, x0, y0, x2, y2)))
        y3 = y1
        fill_flat_bottom(x0, y0, x1, y1, x3, y3)
        fill_flat_top(x1, y1, x3, y3, x2, y2)


def draw_icon_64() -> List[List[Color]]:
    size = 64
    canvas = create_canvas(size, size, TRANSPARENT)

    # Page/sheet rectangle area
    margin = 4
    x0, y0 = margin + 1, margin
    x1, y1 = size - margin, size - margin

    # Fill sheet area white and border dark gray
    fill_rect(canvas, x0, y0 + 1, x1, y1, WHITE)
    draw_rect(canvas, x0, y0 + 1, x1, y1, DARK_GRAY)

    # Excel themed header band on the left
    header_width = 10
    fill_rect(canvas, x0, y0 + 1, x0 + header_width, y1, EXCEL_GREEN)

    # Grid lines inside the sheet
    cell = 8
    # Vertical grid lines
    for gx in range(x0 + header_width + cell, x1, cell):
        for y in range(y0 + 2, y1):
            set_pixel(canvas, gx, y, LIGHT_GRAY)
    # Horizontal grid lines
    for gy in range(y0 + 1 + cell, y1, cell):
        for x in range(x0 + 1, x1):
            set_pixel(canvas, x, gy, LIGHT_GRAY)

    # Consolidation arrows (circular sync) in bottom-right quadrant
    cx, cy = 42, 42
    outer_r = 14
    stroke = 3
    draw_circle_arc(canvas, cx, cy, outer_r, 40, 200, stroke, DEEP_GREEN)
    draw_circle_arc(canvas, cx, cy, outer_r - 4, 220, 20 + 360, stroke, DEEP_GREEN)

    # Arrowheads
    # First arrowhead at ~200 degrees
    angle1 = math.radians(200)
    ax1 = cx + int(round(math.cos(angle1) * (outer_r + 0)))
    ay1 = cy + int(round(math.sin(angle1) * (outer_r + 0)))
    # Triangle pointing along tangent at that angle
    t1 = angle1 + math.pi / 2
    p0 = (ax1, ay1)
    p1 = (ax1 - int(round(math.cos(angle1) * 5)), ay1 - int(round(math.sin(angle1) * 5)))
    p2 = (p1[0] + int(round(math.cos(t1) * 3)), p1[1] + int(round(math.sin(t1) * 3)))
    p3 = (p1[0] - int(round(math.cos(t1) * 3)), p1[1] - int(round(math.sin(t1) * 3)))
    draw_filled_triangle(canvas, p0, p2, p3, DEEP_GREEN)

    # Second arrowhead at ~20 degrees
    angle2 = math.radians(20)
    ax2 = cx + int(round(math.cos(angle2) * (outer_r - 4)))
    ay2 = cy + int(round(math.sin(angle2) * (outer_r - 4)))
    t2 = angle2 - math.pi / 2
    q0 = (ax2, ay2)
    q1 = (ax2 + int(round(math.cos(angle2) * 5)), ay2 + int(round(math.sin(angle2) * 5)))
    q2 = (q1[0] + int(round(math.cos(t2) * 3)), q1[1] + int(round(math.sin(t2) * 3)))
    q3 = (q1[0] - int(round(math.cos(t2) * 3)), q1[1] - int(round(math.sin(t2) * 3)))
    draw_filled_triangle(canvas, q0, q2, q3, DEEP_GREEN)

    return canvas


def rgba_to_bgra_bytes(p: Color) -> bytes:
    r, g, b, a = p
    return bytes((b, g, r, a))


def canvas_to_ico_dib(canvas: List[List[Color]]) -> bytes:
    height = len(canvas)
    width = len(canvas[0]) if height > 0 else 0

    # BITMAPINFOHEADER (40 bytes)
    biSize = 40
    biWidth = width
    biHeight = height * 2  # include XOR and AND mask
    biPlanes = 1
    biBitCount = 32
    biCompression = 0  # BI_RGB
    biSizeImage = width * height * 4
    biXPelsPerMeter = 0
    biYPelsPerMeter = 0
    biClrUsed = 0
    biClrImportant = 0

    header = struct.pack(
        '<IIIHHIIIIII',
        biSize,
        biWidth,
        biHeight,
        biPlanes,
        biBitCount,
        biCompression,
        biSizeImage,
        biXPelsPerMeter,
        biYPelsPerMeter,
        biClrUsed,
        biClrImportant,
    )

    # XOR bitmap (bottom-up rows), 32bpp BGRA
    xor_bytes = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            xor_bytes += rgba_to_bgra_bytes(canvas[y][x])

    # AND mask: 1 bit per pixel (0 = opaque, 1 = transparent), padded to 32-bit per row
    and_row_bytes = ((width + 31) // 32) * 4
    and_bytes = bytearray()
    for y in range(height - 1, -1, -1):
        bits = 0
        bit_count = 0
        row = canvas[y]
        for x in range(width):
            alpha = row[x][3]
            bit = 1 if alpha == 0 else 0  # 1 = transparent
            bits = (bits << 1) | bit
            bit_count += 1
            if bit_count == 8:
                and_bytes.append(bits & 0xFF)
                bits = 0
                bit_count = 0
        if bit_count != 0:
            # Pad the last byte
            bits <<= (8 - bit_count)
            and_bytes.append(bits & 0xFF)
        # Pad row to 32-bit boundary
        pad_len = and_row_bytes - ((width + 7) // 8)
        and_bytes += b'\x00' * pad_len

    return header + xor_bytes + and_bytes


def resize_canvas_nearest(canvas: List[List[Color]], target_w: int, target_h: int) -> List[List[Color]]:
    src_h = len(canvas)
    src_w = len(canvas[0]) if src_h > 0 else 0
    if src_w == 0 or src_h == 0:
        return create_canvas(target_w, target_h)
    out = create_canvas(target_w, target_h)
    for y in range(target_h):
        src_y = int(round((y + 0.5) * src_h / target_h - 0.5))
        src_y = 0 if src_y < 0 else (src_h - 1 if src_y >= src_h else src_y)
        for x in range(target_w):
            src_x = int(round((x + 0.5) * src_w / target_w - 0.5))
            src_x = 0 if src_x < 0 else (src_w - 1 if src_x >= src_w else src_x)
            out[y][x] = canvas[src_y][src_x]
    return out


def write_multi_image_ico(path: str, canvases: List[List[List[Color]]]) -> None:
    # Build DIBs for each canvas
    dibs = [canvas_to_ico_dib(c) for c in canvases]
    widths = [len(c[0]) for c in canvases]
    heights = [len(c) for c in canvases]

    # ICONDIR
    reserved = 0
    icon_type = 1  # ICO
    count = len(dibs)
    icondir = struct.pack('<HHH', reserved, icon_type, count)

    # Calculate offsets
    offset = 6 + 16 * count
    entries = []
    for i, dib in enumerate(dibs):
        bWidth = widths[i] if widths[i] < 256 else 0
        bHeight = heights[i] if heights[i] < 256 else 0
        bColorCount = 0
        bReserved = 0
        wPlanes = 1
        wBitCount = 32
        dwBytesInRes = len(dib)
        dwImageOffset = offset
        entry = struct.pack('<BBBBHHII', bWidth, bHeight, bColorCount, bReserved, wPlanes, wBitCount, dwBytesInRes, dwImageOffset)
        entries.append(entry)
        offset += dwBytesInRes

    with open(path, 'wb') as f:
        f.write(icondir)
        for e in entries:
            f.write(e)
        for dib in dibs:
            f.write(dib)


def main() -> None:
    base64 = draw_icon_64()
    sizes = [64, 48, 32, 24, 16]
    canvases = [base64]
    for s in sizes[1:]:
        canvases.append(resize_canvas_nearest(base64, s, s))
    out_path = '/workspace/employee_billing_updater.ico'
    write_multi_image_ico(out_path, canvases)
    print(f'Wrote multi-size icon to: {out_path}')


if __name__ == '__main__':
    main()