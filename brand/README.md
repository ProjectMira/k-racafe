# kōra — logo kit

The mark is a lowercase **ō** — a monoline ring with a macron — inside a square.
It is drawn as **pure geometry**, not set in a typeface, so every file is
independent of installed fonts and identical at any size.

## Construction

Drawn on a 512 grid. All proportions derive from it, so the mark can be rebuilt
at any scale without redrawing.

| | |
|---|---|
| Canvas | 512 × 512 |
| Ring outer diameter | 230 (45% of canvas) |
| Stroke weight | 38 — ring and macron are identical (monoline) |
| Macron | 168 × 38, 73% of ring width |
| Gap, macron to ring | 50 |
| Glyph height | 318, optically centred |
| Border | 16 standard · 34 for small sizes |

## Colour

| Role | Hex |
|---|---|
| Ink | `#111111` |
| Paper | `#FFFFFF` |
| Brand green | `#2F4A35` |

Site background is warm off-white `#faf8f3`. The square itself is always pure
white — that contrast is deliberate.

## Files

### `svg/` — masters, use these wherever possible

| File | Use |
|---|---|
| `kora-mark.svg` | **primary** — white square, black border, black ō |
| `kora-mark-inverse.svg` | black square, white ō — for dark grounds |
| `kora-mark-green.svg` | green square, white ō |
| `kora-mark-outline.svg` | transparent background, black border and ō |
| `kora-glyph.svg` | the ō alone, no square — stamps, watermarks, patterns |
| `kora-glyph-white.svg` | ō alone, reversed |
| `kora-mark-small.svg` | heavier border, holds at 32–48 px |
| `kora-mark-micro.svg` | no border, enlarged glyph — 16 px only |
| `kora-maskable.svg` | green full-bleed, glyph inside the Android safe zone |

### `png/` — 64 to 2048 px, plus inverse and green at 512/1024

Glyph-only PNGs have a transparent background; the mark PNGs are opaque.

### `favicon/` — drop-in web set

`favicon.ico` (16/32/48 bundled), `favicon.svg`, `apple-touch-icon.png` (180),
`icon-192.png`, `icon-512.png`, `icon-512-maskable.png`, `site.webmanifest`.

### `print/` — vector PDF, 768 pt square, for printers and signage

### `kora.icns` — macOS app/folder icon

## Rules

**Clear space** — keep free space equal to **one quarter of the square's width**
on all sides. Nothing intrudes: no type, no image edge, no other logo.

**Minimum size** — 16 px on screen, 8 mm in print. Below 48 px use
`kora-mark-small.svg`; at 16 px use `kora-mark-micro.svg`. The standard border
disappears at small sizes, which is exactly what those variants fix.

**Never**
- Recolour outside the three brand colours
- Stretch, rotate, or skew — the square is a square
- Add effects: shadows, gradients, glows, strokes, bevels
- Rebuild the ō from a font — the geometry is the logo
- Place the white-square version on a busy photograph; use the inverse or green
- Crowd it — clear space is not optional

## Rebuilding

The geometry lives in the SVG masters. To regenerate the whole kit at different
proportions, edit the constants and re-derive every raster from `kora-mark.svg`
— never upscale a PNG.

## The wordmark

The site sets "kōra" in **Fraunces** (Georgia as fallback). No outlined wordmark
lockup ships here: outlining requires the licensed font, and doing it properly
is a designer's job once the typeface is settled. Until then the mark stands
alone, which is how it was chosen to work.
