#!/usr/bin/env python3
"""kōra — logo kit builder.

The mark is pure geometry (see README.md), so the whole kit derives from the
constants in this file. Edit them, run the script, and every SVG is rebuilt;
PNG and PDF exports follow via rsvg-convert (brew install librsvg).

    python3 brand/build.py check      confirm the constants reproduce brand/svg/ exactly
    python3 brand/build.py explore    write the exploration sets to brand/explorations/
    python3 brand/build.py sheets     flat PNG contact sheets of the explorations, for sharing
    python3 brand/build.py masters    rebuild brand/svg/, brand/png/ and brand/print/

favicon.ico, kora.icns and the social images are not rebuilt here.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path

BRAND = Path(__file__).resolve().parent

INK = "#111111"
PAPER = "#FFFFFF"
GREEN = "#2F4A35"


@dataclass(frozen=True)
class Geometry:
    """Everything sits on a 512 grid and the glyph is optically centred."""

    canvas: int = 512
    ring_d: int = 230      # ring outer diameter, 45% of the canvas
    stroke: int = 38       # ring stroke weight
    gap: int = 50          # macron bottom to ring top
    macron_w: int = 168    # 73% of the ring width
    macron_h: int = 38     # equals the stroke: monoline

    @property
    def glyph_h(self) -> float:
        return self.macron_h + self.gap + self.ring_d

    @property
    def top(self) -> float:
        return (self.canvas - self.glyph_h) / 2

    @property
    def macron_x(self) -> float:
        return (self.canvas - self.macron_w) / 2

    @property
    def ring_cy(self) -> float:
        return self.top + self.macron_h + self.gap + self.ring_d / 2

    @property
    def ring_r(self) -> float:
        return (self.ring_d - self.stroke) / 2


CURRENT = Geometry()


def n(v: float) -> str:
    """Shortest clean number: 97.0 -> 97, 56.32 -> 56.32."""
    return f"{v:g}"


def glyph(g: Geometry, colour: str) -> str:
    return (
        f'<rect x="{n(g.macron_x)}" y="{n(g.top)}" width="{g.macron_w}" '
        f'height="{g.macron_h}" fill="{colour}"/>'
        f'<circle cx="{n(g.canvas / 2)}" cy="{n(g.ring_cy)}" r="{n(g.ring_r)}" '
        f'fill="none" stroke="{colour}" stroke-width="{g.stroke}"/>'
    )


def mark(g: Geometry = CURRENT, *, bg: str | None = None, border: str | None = None,
         border_w: int = 16, ink: str = INK, scale: float = 1) -> str:
    c = g.canvas
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {c} {c}" width="{c}" height="{c}">']
    if bg:
        out.append(f'<rect width="{c}" height="{c}" fill="{bg}"/>')
    if border:
        i = border_w / 2
        out.append(
            f'<rect x="{n(i)}" y="{n(i)}" width="{n(c - border_w)}" height="{n(c - border_w)}" '
            f'fill="none" stroke="{border}" stroke-width="{border_w}"/>'
        )
    body = glyph(g, ink)
    if scale != 1:
        t = c * (1 - scale) / 2
        body = f'<g transform="translate({n(t)},{n(t)}) scale({n(scale)})">{body}</g>'
    out.append(body)
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- masters

MASTERS: dict[str, dict] = {
    "kora-mark":         dict(bg=PAPER, border=INK),
    "kora-mark-inverse": dict(bg=INK, ink=PAPER),
    "kora-mark-green":   dict(bg=GREEN, ink=PAPER),
    "kora-mark-outline": dict(border=INK),
    "kora-glyph":        dict(),
    "kora-glyph-white":  dict(ink=PAPER),
    "kora-mark-small":   dict(bg=PAPER, border=INK, border_w=34),
    "kora-mark-micro":   dict(bg=PAPER, scale=1.3),
    "kora-maskable":     dict(bg=GREEN, ink=PAPER, scale=0.78),
}
PNG_SIZES: dict[str, tuple[int, ...]] = {
    "kora-mark":         (64, 128, 256, 512, 1024, 2048),
    "kora-mark-inverse": (512, 1024),
    "kora-mark-green":   (512, 1024),
    "kora-glyph":        (1024,),
    "kora-glyph-white":  (1024,),
}
PRINT = ("kora-mark", "kora-mark-inverse", "kora-mark-green", "kora-glyph")
PRINT_PX = 1024  # rsvg-convert renders PDF at 96 px/in, so 1024 px = 768 pt


# ----------------------------------------------------------- explorations

@dataclass(frozen=True)
class MacronOption:
    key: str
    label: str
    geometry: Geometry


MACRONS = [
    MacronOption("a", "current", CURRENT),
    MacronOption("b", "a little smaller", replace(CURRENT, macron_w=150, macron_h=34)),
    MacronOption("c", "smaller", replace(CURRENT, macron_w=140, macron_h=30)),
    MacronOption("d", "same width, thinner", replace(CURRENT, macron_h=30)),
]

COLOURS = {
    "red":    "#B8382C",
    "maroon": "#7B2A2A",
    "green":  GREEN,
    "moss":   "#4A7C4E",
    "blue":   "#2F5A96",
    "navy":   "#1F3352",
}


def layouts(colour: str) -> dict[str, dict]:
    return {
        "solid": dict(bg=colour, ink=PAPER),               # colour square, white ō
        "paper": dict(bg=PAPER, border=colour, ink=colour),  # white square, colour rule and ō
        "duo":   dict(bg=PAPER, border=INK, ink=colour),   # white square, ink rule, colour ō
        "glyph": dict(ink=colour),                         # ō alone, transparent
    }


# ------------------------------------------------------------------ output

def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def need_rsvg() -> str:
    exe = shutil.which("rsvg-convert")
    if not exe:
        sys.exit("rsvg-convert not found: brew install librsvg")
    return exe


def png(svg_path: Path, out: Path, size: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([need_rsvg(), "-w", str(size), "-h", str(size), "-o", str(out), str(svg_path)], check=True)


def pdf(svg_path: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([need_rsvg(), "-f", "pdf", "-w", str(PRINT_PX), "-h", str(PRINT_PX),
                    "-o", str(out), str(svg_path)], check=True)


def cmd_check() -> None:
    bad = []
    for name, opts in MASTERS.items():
        path = BRAND / "svg" / f"{name}.svg"
        if path.read_text().strip() != mark(**opts):
            bad.append(name)
    if bad:
        sys.exit("constants do NOT reproduce: " + ", ".join(bad))
    print(f"ok: constants reproduce all {len(MASTERS)} masters in brand/svg/")


def cmd_masters() -> None:
    for name, opts in MASTERS.items():
        write(BRAND / "svg" / f"{name}.svg", mark(**opts))
    for name, sizes in PNG_SIZES.items():
        for s in sizes:
            png(BRAND / "svg" / f"{name}.svg", BRAND / "png" / f"{name}-{s}.png", s)
    for name in PRINT:
        pdf(BRAND / "svg" / f"{name}.svg", BRAND / "print" / f"{name}.pdf")
    print("rebuilt brand/svg, brand/png, brand/print")


def cmd_explore() -> None:
    root = BRAND / "explorations"
    count = 0
    for m in MACRONS:
        p = root / "macron" / f"kora-mark-macron-{m.key}.svg"
        write(p, mark(m.geometry, bg=PAPER, border=INK))
        png(p, p.with_suffix(".png"), 512)
        count += 1
    for cname, hexv in COLOURS.items():
        for lname, opts in layouts(hexv).items():
            p = root / "colour" / f"kora-mark-{cname}-{lname}.svg"
            write(p, mark(**opts))
            png(p, p.with_suffix(".png"), 512)
            count += 1
    print(f"wrote {count} svg + png pairs under brand/explorations/")


SHEET_FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
SHEET_PAPER, SHEET_SOFT, SHEET_LINE = "#faf8f3", "#4a4a46", "#e0dacd"


def nested(svg: str, x: float, y: float, size: float) -> str:
    """Re-wrap a full mark SVG as a nested <svg> so it can sit on a sheet."""
    inner = svg[svg.index(">") + 1:-len("</svg>")]
    return f'<svg x="{n(x)}" y="{n(y)}" width="{n(size)}" height="{n(size)}" viewBox="0 0 512 512">{inner}</svg>'


def sheet(w: float, h: float, title: str, body: list[str]) -> str:
    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(w)} {n(h)}" width="{n(w)}" '
        f'height="{n(h)}" font-family="{SHEET_FONT}">',
        f'<rect width="{n(w)}" height="{n(h)}" fill="{SHEET_PAPER}"/>',
        f'<text x="56" y="72" font-size="20" letter-spacing="3" fill="{GREEN}">{title}</text>',
    ]
    return "".join(head + body + ["</svg>"])


def cmd_sheets() -> None:
    root = BRAND / "explorations"

    # the macron: one row, current first
    tile, gap, pad, top = 300, 44, 56, 112
    w = pad * 2 + len(MACRONS) * tile + (len(MACRONS) - 1) * gap
    h = top + tile + 110
    body = []
    for i, m in enumerate(MACRONS):
        x = pad + i * (tile + gap)
        body.append(nested(mark(m.geometry, bg=PAPER, border=INK), x, top, tile))
        body.append(f'<text x="{x}" y="{top + tile + 44}" font-size="24" fill="{INK}">{m.key.upper()}  {m.label}</text>')
        body.append(f'<text x="{x}" y="{top + tile + 74}" font-size="19" fill="{SHEET_SOFT}">'
                    f'bar {m.geometry.macron_w} × {m.geometry.macron_h}</text>')
    p = root / "macron-sheet.svg"
    write(p, sheet(w, h, "KŌRA · THE MACRON · RING UNCHANGED", body))
    subprocess.run([need_rsvg(), "-o", str(p.with_suffix(".png")), str(p)], check=True)

    # colour: one row per shade, one column per layout
    tile, gap, pad, labw, top = 190, 22, 56, 250, 150
    names = list(layouts(INK).keys())
    w = pad * 2 + labw + len(names) * tile + (len(names) - 1) * gap
    h = top + len(COLOURS) * (tile + gap) - gap + pad
    body = []
    for j, lname in enumerate(names):
        x = pad + labw + j * (tile + gap)
        body.append(f'<text x="{x}" y="{top - 22}" font-size="15" letter-spacing="2" fill="{SHEET_SOFT}">{lname.upper()}</text>')
    for i, (cname, hexv) in enumerate(COLOURS.items()):
        y = top + i * (tile + gap)
        body.append(f'<rect x="{pad}" y="{y + tile // 2 - 12}" width="24" height="24" fill="{hexv}"/>')
        body.append(f'<text x="{pad + 38}" y="{y + tile // 2}" font-size="22" fill="{INK}">{cname}</text>')
        body.append(f'<text x="{pad + 38}" y="{y + tile // 2 + 26}" font-size="16" fill="{SHEET_SOFT}">{hexv}</text>')
        for j, (lname, opts) in enumerate(layouts(hexv).items()):
            x = pad + labw + j * (tile + gap)
            body.append(nested(mark(**opts), x, y, tile))
    p = root / "colour-sheet.svg"
    write(p, sheet(w, h, "KŌRA · COLOUR · SOLID / PAPER / DUO / GLYPH", body))
    subprocess.run([need_rsvg(), "-o", str(p.with_suffix(".png")), str(p)], check=True)
    print("wrote brand/explorations/macron-sheet.png and colour-sheet.png")


if __name__ == "__main__":
    cmds = {"check": cmd_check, "masters": cmd_masters, "explore": cmd_explore, "sheets": cmd_sheets}
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in cmds:
        sys.exit(__doc__)
    cmds[arg]()
