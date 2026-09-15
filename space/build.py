#!/usr/bin/env python3
"""Draw the kōra space drawings.

    python3 space/build.py

Writes floor-plan.svg and island.svg next to this file (and PNGs if a
rasteriser is installed).  Every dimension lives in the PLAN dict below in
feet; change a number there and the drawing, the dimension strings and the
tables all move together.  Nothing here is eyeballed.
"""
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).parent

# ── palette (brand paper + ink, oak for timber, one green) ───────────────
PAPER = "#faf8f3"
INK = "#111111"
GREEN = "#2f4a35"
OAK = "#e6d3b3"
OAK_D = "#cfb389"
STONE = "#f3efe7"
CHILL = "#dbe8ee"
GLASS = "#8fbfd0"
PAVE = "#e9e6df"
STEEL = "#2b2b2b"
MUTE = "#6f6d67"
WALL = "#111111"

# ── the plan, in feet ────────────────────────────────────────────────────
PLAN = dict(
    width=32.0,          # interior clear width (frontage)
    depth=25.0,          # interior clear depth
    boh=6.0,             # back-of-house strip along the back wall
    pavement=8.0,        # outdoor strip in front of the glazing
    door=6.0,            # entrance, centred
    island_w=12.0, island_d=8.0,
    front_ctr=2.5, aisle=3.0, back_bar=2.5,
    shelf_deep=1.17,     # 350 mm open shelving
    chiller_deep=2.5,    # 760 mm multideck
    chiller_len=12.0,    # 3 × 4′ units
    snacks_len=14.0,
    menu_w=12.0,
    island_from_front=5.5,
)


def ftin(ft):
    whole = int(ft)
    inches = round((ft - whole) * 12)
    if inches == 12:
        whole, inches = whole + 1, 0
    s = f"{whole}′"
    if inches:
        s += f"{inches}″"
    return s


def mm(ft):
    return f"{int(round(ft * 304.8 / 10.0) * 10):,} mm"


class Sheet:
    """Tiny SVG writer working in feet."""

    def __init__(self, W, H, scale, ox, oy):
        self.W, self.H, self.s, self.ox, self.oy = W, H, scale, ox, oy
        self.parts = []

    def X(self, ft):
        return round(self.ox + ft * self.s, 1)

    def Y(self, ft):
        return round(self.oy + ft * self.s, 1)

    def L(self, ft):
        return round(ft * self.s, 1)

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1, rx=0, dash=None, op=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' opacity="{op}"' if op else ""
        self.add(f'<rect x="{self.X(x)}" y="{self.Y(y)}" width="{self.L(w)}" height="{self.L(h)}" '
                 f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None, marker=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<line x1="{self.X(x1)}" y1="{self.Y(y1)}" x2="{self.X(x2)}" y2="{self.Y(y2)}" '
                 f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{extra}/>')

    def circle(self, x, y, r_ft, fill="none", stroke=INK, sw=1):
        self.add(f'<circle cx="{self.X(x)}" cy="{self.Y(y)}" r="{self.L(r_ft)}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=11, anchor="middle", weight="400", fill=INK,
             family="sans", tracking=0, rotate=None, italic=False, px=False):
        fam = ("'Fraunces', Georgia, serif" if family == "serif"
               else "'Helvetica Neue', Helvetica, Arial, sans-serif")
        X = x if px else self.X(x)
        Y = y if px else self.Y(y)
        tr = f' transform="rotate({rotate} {X} {Y})"' if rotate is not None else ""
        st = ' font-style="italic"' if italic else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add(f'<text x="{X}" y="{Y}" font-family="{fam}" font-size="{size}" '
                 f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
                 f'letter-spacing="{tracking}"{st}{tr}>{s}</text>')

    def label(self, x, y, s, size=9.5, fill=MUTE, anchor="middle", rotate=None):
        self.text(x, y, s.upper(), size=size, anchor=anchor, weight="600", fill=fill,
                  tracking=1.2, rotate=rotate)

    def dim(self, x1, y1, x2, y2, off, label=None, fill=INK, ext=True, size=10):
        """Dimension line with end ticks.  Horizontal if y1==y2 else vertical.
        `off` is the offset (ft) of the dimension line from the measured edge;
        positive = below / right."""
        lbl = label or ftin(abs(x2 - x1) if y1 == y2 else abs(y2 - y1))
        t = 0.28  # tick half-length, ft
        if y1 == y2:
            yd = y1 + off
            if ext:
                self.line(x1, y1, x1, yd + (t if off > 0 else -t), stroke=fill, sw=0.6)
                self.line(x2, y2, x2, yd + (t if off > 0 else -t), stroke=fill, sw=0.6)
            self.line(x1, yd, x2, yd, stroke=fill, sw=0.8)
            for x in (x1, x2):
                self.line(x - t * 0.6, yd + t * 0.6, x + t * 0.6, yd - t * 0.6, stroke=fill, sw=0.9)
            self.text((x1 + x2) / 2, yd - 0.22, lbl, size=size, fill=fill, weight="500")
        else:
            xd = x1 + off
            if ext:
                self.line(x1, y1, xd + (t if off > 0 else -t), y1, stroke=fill, sw=0.6)
                self.line(x2, y2, xd + (t if off > 0 else -t), y2, stroke=fill, sw=0.6)
            self.line(xd, y1, xd, y2, stroke=fill, sw=0.8)
            for y in (y1, y2):
                self.line(xd - t * 0.6, y + t * 0.6, xd + t * 0.6, y - t * 0.6, stroke=fill, sw=0.9)
            self.text(xd - 0.22, (y1 + y2) / 2, lbl, size=size, fill=fill, weight="500", rotate=-90)

    def svg(self, title, desc):
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H}" '
                f'width="{self.W}" height="{self.H}" role="img" aria-label="{title}">\n'
                f'<title>{title}</title><desc>{desc}</desc>\n'
                '<defs>'
                f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker>'
                f'<pattern id="flute" width="6" height="6" patternUnits="userSpaceOnUse">'
                f'<rect width="6" height="6" fill="{OAK}"/><rect width="2" height="6" fill="{OAK_D}"/></pattern>'
                f'<pattern id="pave" width="18" height="18" patternUnits="userSpaceOnUse">'
                f'<rect width="18" height="18" fill="{PAVE}"/><path d="M0,18 H18 M18,0 V18" stroke="#d8d4cb" stroke-width="1"/></pattern>'
                '</defs>\n'
                f'<rect width="{self.W}" height="{self.H}" fill="{PAPER}"/>\n'
                f'{body}\n</svg>\n')


# ═══════════════════════════════════════════════════════════════════════════
# Floor plan
# ═══════════════════════════════════════════════════════════════════════════
def floor_plan():
    P = PLAN
    s = 22.0
    W, D, B, PV = P["width"], P["depth"], P["boh"], P["pavement"]
    sh = Sheet(1000, 960, s, ox=120, oy=130)
    retail_y = B                      # retail room starts below the BOH strip
    front = D                         # glazing line
    r_depth = D - B                   # retail depth

    # sheet title block
    sh.text(120, 44, "kōra — floor plan", size=24, anchor="start", family="serif", weight="500", px=True)
    sh.text(120, 66, f"Interior {ftin(W)} × {ftin(D)}  ·  {int(W*D)} sq ft  ·  scale 1 ft = {int(s)} px  ·  street at the bottom",
            size=11.5, anchor="start", fill=MUTE, px=True)
    sh.text(880, 44, "SHEET 1 / 2", size=10, anchor="end", weight="600", tracking=1.5, fill=MUTE, px=True)

    # pavement
    sh.rect(-0.75, front, W + 1.5, PV, fill="url(#pave)", stroke="none")

    # floor
    sh.rect(0, retail_y, W, r_depth, fill=STONE, stroke="none")
    sh.rect(0, 0, W, B, fill="#eeebe4", stroke="none")

    # ── back of house ──
    sh.rect(0, 0, 5, B, fill="#e8e4dc", stroke=INK, sw=0.8)            # washroom
    sh.label(2.5, 2.6, "WC", size=9)
    sh.text(2.5, 3.5, ftin(5) + " × " + ftin(B), size=8.5, fill=MUTE)
    sh.line(5, 2.2, 5, 4.2, stroke=PAPER, sw=3)                        # wc door gap
    sh.add(f'<path d="M{sh.X(5)},{sh.Y(4.2)} A{sh.L(2)},{sh.L(2)} 0 0 0 {sh.X(7)},{sh.Y(2.2)}" fill="none" stroke="{INK}" stroke-width="0.6"/>')
    sh.rect(5.5, 0, 7, 2.0, fill="#d9dfe3", stroke=INK, sw=0.7)         # 3-comp sink
    sh.label(9, 1.25, "wash-up · 3-comp sink", size=7.5)
    sh.rect(12.8, 0, 1.6, 1.6, fill="#d9dfe3", stroke=INK, sw=0.7)      # handwash
    sh.label(13.6, 2.4, "hand", size=6.5)
    sh.rect(15, 0, 2.5, 2.5, fill="#d9dfe3", stroke=INK, sw=0.7)        # ice machine
    sh.label(16.25, 1.5, "ice", size=8)
    sh.rect(18, 0, 4, 2.5, fill="#d9dfe3", stroke=INK, sw=0.7)          # chest freezer
    sh.label(20, 1.5, "freezer", size=8)
    sh.rect(22.5, 0, 2.5, 2.5, fill="#d9dfe3", stroke=INK, sw=0.7)      # upright fridge
    sh.label(23.75, 1.5, "fridge", size=8)
    sh.rect(25.5, 0, 6.5, 1.5, fill=OAK, stroke=INK, sw=0.7)            # dry store racking
    sh.label(28.75, 1.0, "dry store", size=8)
    sh.rect(29.5, 3.5, 2.5, 2.5, fill="#d9dfe3", stroke=INK, sw=0.7)    # RO / filtration
    sh.label(30.75, 4.9, "RO", size=8)
    sh.label(16, 4.6, "back of house · staff only", size=8.5)

    # partition wall between BOH and retail, with the door at the left
    sh.line(3.5, B, W, B, stroke=WALL, sw=5)
    sh.line(0, B, 0.5, B, stroke=WALL, sw=5)
    sh.add(f'<path d="M{sh.X(0.5)},{sh.Y(B)} A{sh.L(3)},{sh.L(3)} 0 0 1 {sh.X(3.5)},{sh.Y(B+3)}" fill="none" stroke="{INK}" stroke-width="0.6"/>')
    sh.line(0.5, B, 0.5, B + 3, stroke=INK, sw=1.2)

    # ── back wall: pantry shelving + menu board ──
    sd = P["shelf_deep"]
    sh.rect(4, B, 6, sd, fill=OAK, stroke=INK, sw=0.7)
    sh.rect(22, B, W - 22 - 0.5, sd, fill=OAK, stroke=INK, sw=0.7)
    sh.rect(10, B, 12, sd, fill=OAK_D, stroke=INK, sw=0.7)               # low shelving under the menu
    sh.line(10, B + 0.15, 22, B + 0.15, stroke=INK, sw=2.2)              # menu board (wall-hung)
    sh.label(16, B + 0.9, "menu board above · low pantry shelf below", size=7.5, fill=INK)
    sh.label(7, B + 0.75, "pantry", size=7.5, fill=INK)
    sh.label(26.75, B + 0.75, "pantry · merch", size=7.5, fill=INK)

    # ── left wall: grab & go chillers ──
    cd = P["chiller_deep"]
    cy0 = B + 2
    for i in range(3):
        y = cy0 + i * 4
        sh.rect(0, y, cd, 4, fill=CHILL, stroke=INK, sw=0.8)
        sh.line(cd, y + 0.3, cd, y + 3.7, stroke=GLASS, sw=3)             # open front, lit
    for i, t in enumerate(("drinks", "fresh", "breakfast")):
        sh.label(cd / 2, cy0 + i * 4 + 2.1, t, size=7.5, fill=INK)
    sh.label(-0.9, cy0 + 6, "grab & go · 3 open multidecks", size=8, rotate=-90)
    # BYO cup / cup return, front-left corner
    sh.rect(0, front - 2.5, 2, 2.5, fill=OAK_D, stroke=INK, sw=0.7)
    sh.label(1, front - 1.1, "cup", size=6.5)
    sh.label(1, front - 0.5, "return", size=6.5)

    # ── right wall: dry snacks ──
    sy0 = B + 2
    sh.rect(W - sd, sy0, sd, P["snacks_len"], fill=OAK, stroke=INK, sw=0.7)
    for i in range(1, 7):
        sh.line(W - sd, sy0 + i * P["snacks_len"] / 7, W, sy0 + i * P["snacks_len"] / 7, stroke=OAK_D, sw=0.8)
    sh.label(W + 0.9, sy0 + P["snacks_len"] / 2, "dry snacks · open shelving", size=8, rotate=90)
    sh.rect(W - 2, front - 2.5, 2, 2.5, fill="#d5dccc", stroke=INK, sw=0.7)
    sh.label(W - 1, front - 1.1, "plant", size=6.5)

    # ── island ──
    ix, iw, idp = (W - P["island_w"]) / 2, P["island_w"], P["island_d"]
    iy = front - P["island_from_front"] - idp
    fc, ai, bb = P["front_ctr"], P["aisle"], P["back_bar"]
    sh.rect(ix, iy, iw, idp, fill=STONE, stroke=INK, sw=1.4)
    sh.rect(ix, iy, iw, bb, fill="url(#flute)", stroke=INK, sw=0.9)                 # back bar
    sh.rect(ix, iy + bb + ai, iw, fc, fill="url(#flute)", stroke=INK, sw=0.9)       # front counter
    sh.rect(ix, iy + bb, iw, ai, fill="#e4e0d8", stroke="none")                      # barista aisle
    sh.line(ix, iy + bb, ix, iy + bb + ai, stroke=INK, sw=1.4)                       # closed W end
    sh.line(ix + iw, iy + bb, ix + iw, iy + bb + ai, stroke=INK, sw=0.5, dash="3 3")  # gate, E end
    # equipment on the back bar (drawn as blocks)
    eq = [(0.6, 2.6, "espresso 2-grp"), (3.4, 1.4, "grinders"), (5.0, 1.0, "batch"),
          (6.2, 0.7, "soda"), (7.2, 1.6, "juicer"), (9.0, 0.9, "blender"), (10.2, 1.6, "sink")]
    for off, w, t in eq:
        sh.rect(ix + off, iy + 0.35, w, bb - 0.7, fill="#ffffff", stroke=INK, sw=0.6)
        sh.text(ix + off + w / 2, iy + bb / 2 + 0.12, t, size=6.5, fill=INK)
    # front counter fittings
    sh.rect(ix + 0.3, iy + bb + ai + 0.3, 3.5, fc - 0.6, fill="#ffffff", stroke=INK, sw=0.6)
    sh.text(ix + 2.05, iy + bb + ai + fc / 2 + 0.12, "pastry case", size=6.5)
    sh.rect(ix + 5.6, iy + bb + ai + 0.5, 1.2, fc - 1.0, fill="#ffffff", stroke=INK, sw=0.6)
    sh.text(ix + 6.2, iy + bb + ai + fc / 2 + 0.12, "POS", size=6.5)
    sh.text(ix + 9.6, iy + bb + ai + fc / 2 + 0.12, "pick-up", size=6.5)
    sh.label(ix + iw / 2, iy + bb + ai / 2 + 1.05, "barista aisle", size=7.5, fill=INK)
    # pendants
    for x in (ix + 3, ix + 6, ix + 9):
        sh.circle(x, iy + bb + ai / 2, 0.35, fill="none", stroke=GREEN, sw=1)
        sh.circle(x, iy + bb + ai / 2, 0.08, fill=GREEN, stroke="none")
    # face labels
    sh.label(ix + iw / 2, iy - 0.45, "N · juice & shots face", size=7.5, fill=GREEN)
    sh.label(ix + iw / 2, iy + idp + 0.85, "S · order & pick-up face", size=7.5, fill=GREEN)
    sh.label(ix - 0.5, iy + idp / 2, "W · closed end · mark", size=7, fill=GREEN, rotate=-90)
    sh.label(ix + iw + 0.6, iy + idp / 2, "E · staff gate · lids", size=7, fill=GREEN, rotate=90)

    # ── walls ──
    sh.line(0, 0, W, 0, stroke=WALL, sw=6)                    # back wall
    sh.line(0, 0, 0, front, stroke=WALL, sw=6)                # left wall
    sh.line(W, 0, W, front, stroke=WALL, sw=6)                # right wall
    # front: glazing + door
    dx = (W - P["door"]) / 2
    sh.line(0, front, dx, front, stroke=GLASS, sw=5)
    sh.line(dx + P["door"], front, W, front, stroke=GLASS, sw=5)
    for x in (0, dx, dx + P["door"], W):
        sh.line(x, front - 0.3, x, front + 0.3, stroke=WALL, sw=4)
    # door leaves swinging out
    sh.line(dx, front, dx, front + 3, stroke=INK, sw=1.4)
    sh.line(dx + P["door"], front, dx + P["door"], front + 3, stroke=INK, sw=1.4)
    sh.add(f'<path d="M{sh.X(dx)},{sh.Y(front+3)} A{sh.L(3)},{sh.L(3)} 0 0 0 {sh.X(dx+3)},{sh.Y(front)}" fill="none" stroke="{INK}" stroke-width="0.6"/>')
    sh.add(f'<path d="M{sh.X(dx+6)},{sh.Y(front+3)} A{sh.L(3)},{sh.L(3)} 0 0 1 {sh.X(dx+3)},{sh.Y(front)}" fill="none" stroke="{INK}" stroke-width="0.6"/>')
    sh.label(W / 2, front + 3.7, "entrance · double glazed door", size=7.5)
    sh.label(6.5, front - 0.6, "full-height glazing", size=7)
    sh.label(W - 6.5, front - 0.6, "full-height glazing", size=7)

    # ── pavement seating ──
    for x in (4.0, 9.0, W - 9.0, W - 4.0):
        y = front + 5.2
        sh.circle(x, y, 1.0, fill=OAK, stroke=INK, sw=0.7)
        for cx in (x - 2.0, x + 2.0):
            sh.rect(cx - 0.7, y - 0.7, 1.4, 1.4, fill=GREEN, stroke="none", rx=2)
    for (x0, x1) in ((2.5, 11.0), (W - 11.0, W - 2.5)):
        sh.rect(x0, front + 0.6, x1 - x0, 1.0, fill="#cfd8c4", stroke=INK, sw=0.6)  # low planter
    for x0 in (-0.5, W - 1.5):
        sh.rect(x0, front + 1, 2.0, 6.0, fill="#cfd8c4", stroke=INK, sw=0.6)       # end planters
    sh.label(W / 2, front + 7.2, "pavement · 4 two-tops · planters as the buffer", size=8)

    # ── the kora loop ──
    pts = [(W / 2 - 1.2, front + 1.5), (W / 2 - 1.2, front - 2.2), (4.2, front - 2.2), (4.2, B + 3.0),
           (W - 6.2, B + 3.0), (W - 6.2, front - 3.4), (W / 2 + 1.2, front - 3.4),
           (W / 2 + 1.2, front + 1.5)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{sh.X(x)},{sh.Y(y)}" for i, (x, y) in enumerate(pts))
    sh.add(f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="6 5" '
           f'stroke-linejoin="round" marker-end="url(#arrow)" opacity="0.9"/>')
    sh.text(3.3, B + 9.6, "the kora", size=13, family="serif", italic=True, fill=GREEN, rotate=-90)
    sh.text(W / 2 - 1.9, front + 1.3, "in", size=9, family="serif", italic=True, fill=GREEN, anchor="end")
    sh.text(W / 2 + 1.9, front + 1.3, "out", size=9, family="serif", italic=True, fill=GREEN, anchor="start")
    sh.text(W - 5.3, B + 9.6, "one loop", size=13, family="serif", italic=True, fill=GREEN, rotate=90)

    # ── dimensions ──
    sh.dim(0, 0, W, 0, -1.6, fill=INK)                                  # overall width (top)
    sh.dim(W, 0, W, D, 3.6, fill=INK)                                   # overall depth (right)
    sh.dim(W, 0, W, B, 2.2, fill=MUTE, size=9)                          # BOH
    sh.dim(W, B, W, D, 2.2, fill=MUTE, size=9)                          # retail
    sh.dim(ix, iy + idp, ix + iw, iy + idp, 1.8, fill=GREEN)            # island length
    sh.dim(ix, iy, ix, iy + idp, -1.2, fill=GREEN)                      # island depth
    sh.dim(0, front - 0.9, ix, front - 0.9, -1.0, fill=MUTE, size=8.5, ext=False)      # left aisle (wall to island)
    sh.dim(ix + iw, front - 0.9, W, front - 0.9, -1.0, fill=MUTE, size=8.5, ext=False)  # right aisle
    sh.dim(ix + iw + 0.6, iy + idp, ix + iw + 0.6, front, 0, fill=MUTE, size=8.5, ext=False)  # front aisle
    sh.dim(ix + iw + 0.6, B + sd, ix + iw + 0.6, iy, 0, fill=MUTE, size=8.5, ext=False)       # back aisle
    sh.dim(dx, front, dx + P["door"], front, 4.6, fill=MUTE, size=9, ext=False)          # door
    sh.dim(-0.75, front, -0.75, front + PV, -1.6, fill=MUTE, size=9)                     # pavement
    sh.dim(cd, cy0, cd, cy0 + P["chiller_len"], 0.9, fill=MUTE, size=8.5, ext=False)          # chillers
    sh.dim(W - sd, sy0, W - sd, sy0 + P["snacks_len"], -0.9, fill=MUTE, size=8.5, ext=False)  # snacks

    # ── legend / key ──
    kx, ky = 120, 905
    items = [(OAK, "timber shelving · pale oak"), (CHILL, "refrigerated display"),
             ("url(#flute)", "fluted oak counter, stone top"), (GLASS, "glazing"), (GREEN, "customer loop")]
    for i, (f, t) in enumerate(items):
        x = kx + i * 176
        sh.add(f'<rect x="{x}" y="{ky}" width="16" height="12" fill="{f}" stroke="{INK}" stroke-width="0.6"/>')
        sh.text(x + 22, ky + 10.5, t, size=10, anchor="start", fill=MUTE, px=True)
    sh.text(880, 66, "north = back wall", size=10, anchor="end", fill=MUTE, px=True)
    return sh.svg("kōra floor plan, 32 by 25 feet, street at the bottom",
                  "Grab-and-go café: central island bar, grab-and-go chillers on the left wall, "
                  "dry snacks on the right, menu and pantry on the back wall, "
                  "back of house behind, pavement seating in front.")


# ═══════════════════════════════════════════════════════════════════════════
# Island detail
# ═══════════════════════════════════════════════════════════════════════════
def island():
    P = PLAN
    s = 52.0
    iw, idp = P["island_w"], P["island_d"]
    fc, ai, bb = P["front_ctr"], P["aisle"], P["back_bar"]
    sh = Sheet(1000, 900, s, ox=190, oy=150)

    sh.text(120, 44, "kōra — the island", size=24, anchor="start", family="serif", weight="500", px=True)
    sh.text(120, 66, f"{ftin(iw)} × {ftin(idp)} ({mm(iw)} × {mm(idp)})  ·  counters 36″ / 915 mm high  ·  four faces, four jobs",
            size=11.5, anchor="start", fill=MUTE, px=True)
    sh.text(880, 44, "SHEET 2 / 2", size=10, anchor="end", weight="600", tracking=1.5, fill=MUTE, px=True)

    sh.rect(0, 0, iw, idp, fill=STONE, stroke=INK, sw=1.6)
    sh.rect(0, 0, iw, bb, fill="url(#flute)", stroke=INK, sw=1)
    sh.rect(0, bb + ai, iw, fc, fill="url(#flute)", stroke=INK, sw=1)
    sh.rect(0, bb, iw, ai, fill="#e4e0d8", stroke="none")
    sh.line(0, bb, 0, bb + ai, stroke=INK, sw=1.8)
    sh.line(iw, bb, iw, bb + ai, stroke=INK, sw=0.8, dash="5 4")
    sh.label(iw / 2, bb + ai / 2 + 0.5, "barista aisle · anti-fatigue mat · under-counter fridges both sides", size=8.5, fill=INK)

    # back bar equipment, with real widths
    eq = [(0.5, 2.6, "espresso", "2-group · 780 mm"), (3.3, 0.65, "grinder", "espresso"), (4.05, 0.65, "grinder", "filter"),
          (4.9, 1.0, "batch brew", "filter coffee"), (6.1, 0.7, "soda", "sparkling tap"),
          (7.1, 1.6, "cold press", "juicer"), (8.9, 0.9, "blender", "shots · shakes"), (10.1, 1.6, "sink", "2-comp + hand")]
    for off, w, t, t2 in eq:
        sh.rect(off, 0.3, w, bb - 0.6, fill="#ffffff", stroke=INK, sw=0.7)
        sh.text(off + w / 2, bb / 2 - 0.02, t, size=8, weight="600")
        sh.text(off + w / 2, bb / 2 + 0.3, t2, size=6.5, fill=MUTE)
    # north face: bottle fridge under the counter
    sh.line(0.4, 0.05, 11.6, 0.05, stroke=GLASS, sw=3)
    sh.label(iw / 2, -0.55, "N · juice & shots face — glass-door bottle fridge below, shot ledge above", size=8, fill=GREEN)

    # front counter
    sh.rect(0.3, bb + ai + 0.3, 3.5, fc - 0.6, fill="#ffffff", stroke=INK, sw=0.7)
    sh.text(2.05, bb + ai + fc / 2 - 0.02, "pastry case", size=8, weight="600")
    sh.text(2.05, bb + ai + fc / 2 + 0.3, "3′6″ · glass, 3 tiers", size=6.5, fill=MUTE)
    sh.rect(5.4, bb + ai + 0.5, 1.4, fc - 1.0, fill="#ffffff", stroke=INK, sw=0.7)
    sh.text(6.1, bb + ai + fc / 2 - 0.02, "POS", size=8, weight="600")
    sh.text(6.1, bb + ai + fc / 2 + 0.3, "+ card reader", size=6.5, fill=MUTE)
    sh.rect(7.6, bb + ai + 0.3, 4.1, fc - 0.6, fill="none", stroke=INK, sw=0.5, dash="3 3")
    sh.text(9.65, bb + ai + fc / 2 - 0.02, "pick-up", size=8, weight="600")
    sh.text(9.65, bb + ai + fc / 2 + 0.3, "cups land here", size=6.5, fill=MUTE)
    sh.label(iw / 2, idp + 0.75, "S · order & pick-up face — the one customers see first", size=8, fill=GREEN)
    sh.label(-0.55, idp / 2, "W · closed end — house mark, BYO-cup sign", size=8, fill=GREEN, rotate=-90)
    sh.label(iw + 0.6, idp / 2, "E · staff gate — lids, sleeves, napkins on a shelf", size=8, fill=GREEN, rotate=90)

    # pendants
    for x in (3, 6, 9):
        sh.circle(x, bb + ai / 2 - 0.7, 0.3, stroke=GREEN, sw=1)
        sh.circle(x, bb + ai / 2 - 0.7, 0.07, fill=GREEN, stroke="none")
    sh.text(6, bb + ai / 2 - 0.15, "3 pendants at 7′ AFF, 3′ apart", size=7, fill=GREEN)

    # dimensions
    sh.dim(0, idp, iw, idp, 1.5, fill=INK)
    sh.dim(0, 0, 0, idp, -1.4, fill=INK)
    sh.dim(iw, 0, iw, bb, 1.4, fill=MUTE, size=9)
    sh.dim(iw, bb, iw, bb + ai, 1.4, fill=MUTE, size=9)
    sh.dim(iw, bb + ai, iw, idp, 1.4, fill=MUTE, size=9)
    sh.dim(0.3, idp + 0.3, 3.8, idp + 0.3, 0.6, fill=MUTE, size=8.5, ext=False)
    sh.dim(0.5, -0.3, 3.1, -0.3, -0.6, fill=MUTE, size=8.5, ext=False, label="espresso · 780 mm")

    # heights table (px, below the plan)
    ty = 700
    rows = [("Counter tops (both)", "36″ · 915 mm", "honed pale limestone or white terrazzo, 30 mm"),
            ("Counter fronts", "fluted white oak", "vertical flutes 30 mm pitch, clear matte lacquer"),
            ("Pastry case top", "≈ 52″ · 1,320 mm", "sits on the front counter, 3 tiers"),
            ("Espresso machine top", "≈ 56″ · 1,420 mm", "keeps the menu board visible from the door"),
            ("Pendants", "84″ · 2,135 mm AFF", "three, opal glass, 2700–3000 K"),
            ("Plumbing", "at the island", "2-comp sink, hand sink, floor drain, water + drain run under the slab")]
    sh.text(120, ty, "HEIGHTS & FINISHES", size=9.5, anchor="start", weight="600", tracking=1.5, fill=MUTE, px=True)
    for i, (a, b, c) in enumerate(rows):
        y = ty + 22 + i * 20
        sh.text(120, y, a, size=11, anchor="start", weight="600", px=True)
        sh.text(330, y, b, size=11, anchor="start", px=True)
        sh.text(490, y, c, size=10.5, anchor="start", fill=MUTE, px=True)
    return sh.svg("kōra island detail, 12 by 8 feet",
                  "Central island bar: front order counter with pastry case and POS, a 3-foot "
                  "barista aisle, a back bar carrying the espresso machine, grinders, batch brewer, "
                  "sparkling tap, cold-press juicer, blender and sinks; the north face serves juice and shots.")


def rasterise(svg_path, png_path, width):
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", str(width), "-o", str(png_path), str(svg_path)], check=True)
        return True
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width)
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    out = {"floor-plan.svg": floor_plan(), "island.svg": island()}
    for name, svg in out.items():
        (HERE / name).write_text(svg, encoding="utf-8")
        print("wrote", HERE / name)
    for name in out:
        png = HERE / name.replace(".svg", ".png")
        if rasterise(HERE / name, png, 2000):
            print("wrote", png)
        else:
            print("no rasteriser found (brew install librsvg) — skipped", png.name)
