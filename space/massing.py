#!/usr/bin/env python3
"""Build a labelled 3D massing view of the café from PLAN in build.py.

    python3 space/massing.py

Writes massing.svg / massing.png: a front-top cutaway of the retail room with
every fixture as a block at its real position and size.  render.py feeds it to
the image model as the geometry reference, so a render cannot drift from the
plan the way it can from a 2D drawing.
"""
import math
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from build import PLAN, PAPER, INK, GREEN, OAK, OAK_D, STONE, CHILL, GLASS, PAVE, MUTE  # noqa: E402

P = PLAN
W = P["width"]
RD = P["depth"] - P["boh"]          # retail depth, 19 ft
PV = P["pavement"]
S = 44.0                            # px per ft at the front edge
PHI = math.radians(63)          # steep enough to see the aisle floor between the two counters
SIN, COS = math.sin(PHI), math.cos(PHI)
PERSP = 0.22
CX, CY = 1000.0, 1120.0
H_WALL = 10.0
H_CUT = 4.5                         # side walls and glazing cut at chest height


def proj(x, d, z):
    """x across (0..W), d = distance back from the glazing (pavement is negative), z up."""
    k = 1 - PERSP * (d + PV) / (RD + PV)
    return (round(CX + (x - W / 2) * k * S, 1), round(CY - (d * SIN + z * COS) * k * S, 1))


def poly(pts, fill, stroke=INK, sw=0.8, op=None):
    d = " ".join(f"{x},{y}" for x, y in pts)
    o = f' opacity="{op}"' if op else ""
    return f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{o}/>'


def box(x, d, w, dd, h, fill, top=None, z0=0.0, sw=0.8):
    """A block with its footprint x..x+w, d..d+dd, from z0 to z0+h."""
    top = top or fill
    out = []
    cx = x + w / 2
    if cx < W / 2:   # right side face visible
        out.append(poly([proj(x + w, d, z0), proj(x + w, d + dd, z0), proj(x + w, d + dd, z0 + h), proj(x + w, d, z0 + h)], shade(fill), sw=sw))
    else:            # left side face visible
        out.append(poly([proj(x, d, z0), proj(x, d + dd, z0), proj(x, d + dd, z0 + h), proj(x, d, z0 + h)], shade(fill), sw=sw))
    out.append(poly([proj(x, d + dd, z0 + h), proj(x + w, d + dd, z0 + h), proj(x + w, d, z0 + h), proj(x, d, z0 + h)], top, sw=sw))
    out.append(poly([proj(x, d, z0), proj(x + w, d, z0), proj(x + w, d, z0 + h), proj(x, d, z0 + h)], fill, sw=sw))
    return "\n".join(out)


def shade(hexcol, f=0.86):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def label(x, d, z, text, size=13, fill=INK, weight="700", anchor="middle"):
    X, Y = proj(x, d, z)
    t = text.replace("&", "&amp;")
    return (f'<text x="{X}" y="{Y}" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="1">{t}</text>')


def build():
    sd, cd = P["shelf_deep"], P["chiller_deep"]
    parts = []
    A = parts.append

    # pavement and floor
    A(poly([proj(-1, -PV, 0), proj(W + 1, -PV, 0), proj(W + 1, 0, 0), proj(-1, 0, 0)], PAVE, stroke="none"))
    A(poly([proj(0, 0, 0), proj(W, 0, 0), proj(W, RD, 0), proj(0, RD, 0)], STONE, stroke="none"))
    # back wall (full height) and side walls cut at chest height
    A(poly([proj(0, RD, 0), proj(W, RD, 0), proj(W, RD, H_WALL), proj(0, RD, H_WALL)], "#efece5"))
    A(poly([proj(0, 0, 0), proj(0, RD, 0), proj(0, RD, H_CUT), proj(0, 0, H_CUT)], "#e2ded6"))
    A(poly([proj(W, 0, 0), proj(W, RD, 0), proj(W, RD, H_CUT), proj(W, 0, H_CUT)], "#e2ded6"))

    # ── back wall fixtures (drawn first: furthest) ──
    dback = RD - sd
    A(box(0.5, RD - 0.15, 3, 0.15, 7, "#d9cbb0"))                                  # BOH door
    A(label(2, RD, 7.6, "DOOR TO BACK OF HOUSE", 11))
    A(box(4, dback, 6, sd, 7.5, OAK))                                                # tall pantry L
    A(box(22, dback, W - 22 - 0.5, sd, 7.5, OAK))                                    # tall pantry R
    A(box(10, dback, 12, sd, 3.5, OAK_D))                                            # low shelf under menu
    A(box(10, RD - 0.2, 12, 0.2, 3, "#1c1c1c", z0=6.5))                              # menu board
    A(label(16, RD, 8.15, "MENU BOARD", 15, fill="#ffffff"))
    A(label(7, dback, 8.1, "PANTRY SHELVING", 11))
    A(label(26.75, dback, 8.1, "PANTRY SHELVING · MERCH", 11))
    A(label(16, dback, 4.1, "LOW PANTRY SHELF", 10))

    # ── left wall: chillers (start 2 ft from the back wall) ──
    cy0 = RD - 2
    for i in range(3):
        d0 = cy0 - (i + 1) * 4
        A(box(0, d0, cd, 4, 6.5, CHILL, top=OAK))
        A(poly([proj(cd, d0 + 0.3, 0.6), proj(cd, d0 + 3.7, 0.6), proj(cd, d0 + 3.7, 5.8), proj(cd, d0 + 0.3, 5.8)], "#b9d5e2", stroke=GLASS, sw=1.2))
    A(box(cd - 0.35, cy0 - 12, 0.35, 12, 1.0, "#ffffff", z0=6.5))                    # lightbox header on the front edge
    A(label(-0.6, cy0 - 6, 3.2, "GRAB & GO CHILLERS →", 13, anchor="end"))
    A(label(-0.6, cy0 - 6, 2.3, "3 open multidecks: drinks · fresh · breakfast", 10, fill=MUTE, anchor="end"))
    A(label(-0.6, cy0 - 6, 1.5, "white lightbox sign on top", 10, fill=MUTE, anchor="end"))

    # ── right wall: dry-snacks shelving ──
    A(box(W - sd, cy0 - 14, sd, 14, 7.5, OAK))
    A(label(W + 0.6, cy0 - 7, 3.2, "← DRY SNACKS SHELVING", 13, anchor="start"))
    A(label(W + 0.6, cy0 - 7, 2.3, "14 ft of open oak shelving, lit, 7 shelves", 10, fill=MUTE, anchor="start"))

    # ── island: two counters with a barista aisle between ──
    ix, iw, idp = (W - P["island_w"]) / 2, P["island_w"], P["island_d"]
    d_front = P["island_from_front"]                  # front counter face
    fc, ai, bb = P["front_ctr"], P["aisle"], P["back_bar"]
    d_back_bar = d_front + fc + ai
    A(box(ix, d_back_bar, iw, bb, 3.0, OAK_D, top=STONE))                            # back bar
    for off, w, h, t in ((0.6, 2.6, 1.6, "ESPRESSO"), (3.4, 0.65, 1.8, ""), (4.1, 0.65, 1.8, "GRINDERS"),
                         (5.0, 1.0, 1.5, "BATCH"), (7.2, 1.6, 1.7, "JUICER"), (9.0, 0.9, 1.4, "BLENDER"), (10.2, 1.6, 0.3, "SINK")):
        A(box(ix + off, d_back_bar + 0.4, w, bb - 0.8, h, "#f4f4f2", z0=3.0))
        if t:
            A(label(ix + off + w / 2, d_back_bar + 0.4, 3.0 + h + 0.5, t, 9))
    A(poly([proj(ix, d_front + fc, 0), proj(ix + iw, d_front + fc, 0), proj(ix + iw, d_back_bar, 0), proj(ix, d_back_bar, 0)], "#c9c3b7", stroke="none"))
    A(label(ix + iw / 2, d_front + fc + ai / 2, 0.05, "BARISTA AISLE (walkway between the two counters)", 10, fill=MUTE))
    A(box(ix, d_front, iw, fc, 3.0, OAK_D, top=STONE))                               # front counter
    A(box(ix + 0.3, d_front + 0.3, 3.5, fc - 0.6, 1.3, "#e8f1f5", z0=3.0))          # pastry case
    A(label(ix + 2.05, d_front, 4.9, "PASTRY CASE", 9))
    A(box(ix + 5.6, d_front + 0.6, 1.2, fc - 1.2, 0.9, "#333333", z0=3.0))          # POS
    A(label(ix + 6.2, d_front, 4.5, "TILL", 9))
    A(label(ix + 9.6, d_front, 3.6, "PICK-UP", 9))
    A(label(ix + iw / 2, d_front, 2.0, "ISLAND · FRONT COUNTER (fluted oak, stone top)", 11, fill="#ffffff"))
    A(label(ix + iw / 2, d_back_bar, 2.0, "BACK BAR (equipment)", 10, fill="#ffffff"))
    for x in (ix + 3, ix + 6, ix + 9):                                                # pendants
        X, Y = proj(x, d_front + fc + ai / 2, 8.6)
        A(f'<circle cx="{X}" cy="{Y}" r="9" fill="#fff7dc" stroke="{INK}" stroke-width="0.8"/>')
        X2, Y2 = proj(x, d_front + fc + ai / 2, H_WALL)
        A(f'<line x1="{X}" y1="{Y - 9}" x2="{X2}" y2="{Y2}" stroke="{INK}" stroke-width="0.6"/>')

    # ── front corners ──
    A(box(0, 0, 2, 2.5, 3.5, OAK_D))
    A(label(1, 0, 3.9, "CUP RETURN", 8))
    A(box(W - 2, 0, 2, 2.5, 4.5, "#8fa88a"))
    A(label(W - 1, 0, 4.9, "PLANT", 8))

    # ── glazing, cut at chest height; door centred ──
    dx = (W - P["door"]) / 2
    for x0, x1 in ((0, dx), (dx + P["door"], W)):
        A(poly([proj(x0, 0, 0), proj(x1, 0, 0), proj(x1, 0, H_CUT), proj(x0, 0, H_CUT)], "#cfe3ea", stroke=GLASS, sw=1.5, op=0.55))
    for x in (0, dx, dx + P["door"], W):
        A(box(x - 0.15, -0.15, 0.3, 0.3, H_CUT, INK))
    A(poly([proj(dx, 0, 0), proj(dx + P["door"], 0, 0), proj(dx + P["door"], 0, H_CUT), proj(dx, 0, H_CUT)], "none", stroke=INK, sw=1.6))
    A(label(W / 2, -1.0, 0.1, "ENTRANCE · DOUBLE GLASS DOOR (glazing full height, cut here)", 10))
    A(label(6.5, 0, H_CUT + 0.5, "FULL-HEIGHT GLAZING", 9, fill=MUTE))
    A(label(W - 6.5, 0, H_CUT + 0.5, "FULL-HEIGHT GLAZING", 9, fill=MUTE))

    # ── pavement: 4 two-tops, planters ──
    for x0, x1 in ((2.5, 11.0), (W - 11.0, W - 2.5)):
        A(box(x0, -1.6, x1 - x0, 1.0, 1.5, "#9fb59a"))                                # low planters at the glass
    for x in (4.0, 9.0, W - 9.0, W - 4.0):
        d0 = -5.2
        for cx in (x - 2.0, x + 2.0):
            A(box(cx - 0.7, d0 - 0.7, 1.4, 1.4, 1.5, GREEN))
        A(box(x - 1.0, d0 - 1.0, 2.0, 2.0, 2.4, OAK, top=OAK))
    for x0 in (-0.5, W - 1.5):
        A(box(x0, -7.0, 2.0, 6.0, 2.5, "#9fb59a"))
    A(label(W / 2, -7.5, 0.1, "PAVEMENT · FOUR TWO-TOPS · PLANTERS AS THE BUFFER", 11, fill=MUTE))

    # title
    body = "\n".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1400" width="2000" height="1400" role="img" '
            f'aria-label="kōra massing model, front-top cutaway">\n<rect width="2000" height="1400" fill="{PAPER}"/>\n'
            f'<text x="60" y="70" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="{INK}">'
            f'kōra — 3D massing from the floor plan · interior {int(W)} × {int(RD)} ft · back of house behind the back wall</text>\n'
            f'<text x="60" y="104" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="18" fill="{MUTE}">'
            f'Every block is at its real position and size. Walls cut at chest height. Street at the bottom.</text>\n'
            f'{body}\n</svg>\n')


if __name__ == "__main__":
    svg = HERE / "massing.svg"
    svg.write_text(build(), encoding="utf-8")
    print("wrote", svg)
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", "2000", "-o", str(HERE / "massing.png"), str(svg)], check=True)
        print("wrote", HERE / "massing.png")
