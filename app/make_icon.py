"""Maakt icon.ico (oranje tegel met een witte schuine streep) zonder extra packages."""
import math
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / "icon.ico"
ACCENT = (0xC8, 0x66, 0x3A)  # zelfde oranje als in de app
WHITE = (0xFF, 0xFF, 0xFF)


def render(size):
    px = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]
    r = size * 0.22
    for y in range(size):
        for x in range(size):
            # afgeronde rechthoek
            cx = min(max(x + 0.5, r), size - r)
            cy = min(max(y + 0.5, r), size - r)
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            a = max(0.0, min(1.0, r - d + 0.5))
            if a <= 0:
                continue
            # witte schuine streep "/"
            t = size * 0.13
            x1, y1 = size * 0.62, size * 0.22
            x2, y2 = size * 0.38, size * 0.78
            vx, vy = x2 - x1, y2 - y1
            L2 = vx * vx + vy * vy
            u = max(0.0, min(1.0, ((x + 0.5 - x1) * vx + (y + 0.5 - y1) * vy) / L2))
            dist = math.hypot(x + 0.5 - (x1 + u * vx), y + 0.5 - (y1 + u * vy))
            s = max(0.0, min(1.0, t / 2 - dist + 0.5))
            col = tuple(int(ACCENT[i] * (1 - s) + WHITE[i] * s) for i in range(3))
            px[y][x] = (col[0], col[1], col[2], int(255 * a))
    return px


def bmp_image(size):
    px = render(size)
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, size * size * 4, 0, 0, 0, 0)
    data = bytearray()
    for y in range(size - 1, -1, -1):  # bottom-up
        for x in range(size):
            r, g, b, a = px[y][x]
            data += bytes((b, g, r, a))
    mask_row = ((size + 31) // 32) * 4
    mask = bytes(mask_row * size)
    return header + bytes(data) + mask


def png_image(size):
    """PNG voor Linux en macOS (die gebruiken geen .ico)."""
    import zlib

    px = render(size)
    raw = b"".join(b"\x00" + bytes(c for p in row for c in p) for row in px)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def main():
    png = OUT.with_name("icon.png")
    png.write_bytes(png_image(256))
    print(f"{png}")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [bmp_image(s) for s in sizes]
    ico = bytearray(struct.pack("<HHH", 0, 1, len(sizes)))
    offset = 6 + 16 * len(sizes)
    for s, img in zip(sizes, images):
        ico += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(img), offset)
        offset += len(img)
    for img in images:
        ico += img
    OUT.write_bytes(ico)
    print(f"{OUT} ({len(ico)} bytes)")


if __name__ == "__main__":
    main()
