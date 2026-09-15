---
name: kora-space-prompts
description: Write photoreal interior and exterior render prompts for the kōra café space — walls, the central island, the street front, isometric overviews — ready to paste into ChatGPT or any image model. Use when asked for renders, visualisations, mood images or "what the café should look like", or when a new view of the space is needed that matches the existing set. Sister skill to kora-shot-prompts (drinks).
---

# kōra space-render prompts

Produces paste-ready prompts for photoreal renders of the café, and renders
them: `python3 space/render.py [view numbers]` calls Gemini
(`gemini-3-pro-image`, key in `~/.zshrc`) and writes `space/renders/`. Prompts
can also be pasted into ChatGPT or any image model by hand.
The plan and the material palette are fixed; every prompt inherits them so
ten renders read as one café.

## Source of truth

| What | Where |
|---|---|
| Floor plan and island, with dimensions | `space/floor-plan.svg`, `space/island.svg` (regenerate with `python3 space/build.py`; numbers live in `PLAN`) |
| The brief: look, feel, size, what the board says | `space/README.md` |
| The existing prompt set (10 views) | `space/render-prompts.md` |
| The renderer and the images | `space/render.py`, `space/renders/` (each PNG has a `.json` with its exact prompt) |
| The geometry reference | `space/massing.png` from `space/massing.py` — a labelled 3D block model of the plan; the renderer attaches it to every view |
| Reference board | https://www.pinterest.com/tashilhatso/k%C5%8Dra-cafe/ |

Read `space/README.md` before writing a new view. If the plan changes,
change `PLAN` in `space/build.py` first, then the prompts.

## Space constants — never vary these

| | |
|---|---|
| Room | 32 ft wide × 19 ft deep retail, 6 ft back of house behind, full-height glass front, street at the front |
| Island | 12 × 8 ft, centred, 5 ft 6 in from the glass. South face orders, north face juice & shots, west end closed, east end staff gate |
| Left wall | three 4 ft open multideck chillers in an oak surround — GRAB & GO (DRINKS · FRESH · BREAKFAST) |
| Back wall | 12 ft menu board, centred, over a low shelf; tall pantry shelving either side; BOH door far left |
| Right wall | 14 ft of open oak shelving — DRY SNACKS |
| Outside | 8 ft pavement, two two-tops each side of the door, planters as the buffer |
| Timber | pale white oak, matte. Never walnut, never orange, never reclaimed |
| Stone | honed pale limestone or white terrazzo tops |
| Metal | matte black powder-coated steel — shelf frames, glazing frames |
| Walls / floor | warm off-white lime plaster; pale oak-look porcelain plank |
| Accent | deep forest green `#2f4a35`, only on fascia, outdoor chairs, small signs |
| Signage | black capitals on white backlit panels; small black labels on shelves |
| Light | 3000 K, LED strip under every shelf, three opal pendants over the island, daylight from the front |
| Mood | grocer, not lounge. Product is the decor. Tidy, stocked, bright, quick |

**Anti-brand — never generate:** exposed brick, burlap, wicker baskets,
coffee sacks, scattered beans, chalkboards with drawings, neon, Edison
bulbs, sofas, dark moody grading, walnut or teak, terracotta floors,
hanging plants everywhere, readable brand names, the `ō` mark (composite
it afterwards from `brand/svg/`).

## The formula

Every prompt = **scene lock** + **view**. The scene lock is the paragraph at
the top of `space/render-prompts.md`; paste it verbatim. The view paragraph
fills six slots in flowing prose, 90–140 words:

1. **Shot** — `A photorealistic interior photograph…` or `…isometric cutaway render…`
2. **Position** — which wall or face, from where, straight on or angled
3. **The built thing** — its size in feet, its materials from the table above
4. **What's on it** — stocked, in rows, named products from the menu (cold-pressed juice in orange, red, green, gold; fruit cups; kraft snack bags; white cups)
5. **Signs** — at most one or two words in capitals, named exactly
6. **Camera and finish** — lens (28/35mm), height (chest/eye), ratio, `natural colour, fine grain`

## Camera by view

| View | Fragment |
|---|---|
| Wall elevation | `camera at chest height, straight on, 35mm, 3:2` |
| Island end | `straight on from the aisle, 35mm, 2:3 portrait` |
| From the door | `just inside the open door, eye height, 28mm, 3:2` |
| Street front | `straight on from across the street, eye height, 35mm, 16:9` |
| Overview | `isometric cutaway from above and slightly in front, walls cut at chest height, 3:2` |
| Detail | `100mm macro, f/4, one shelf, background melted` |

## Consistency workflow

1. Generate the overview (prompt 1) first: `python3 space/render.py 1`. It
   attaches `massing.png` and `floor-plan.png` as the geometry references.
   Words alone don't hold the layout; the block model does.
2. Then the rest: `python3 space/render.py 2 3 4 5 6 7 8 9 10`. Each attaches
   the plan and the finished view 1 automatically.
3. To add a view, add a `## 11 · Name` section to `render-prompts.md` in the
   same shape (blockquote body, ratio named in the text) and render `11`.
4. Change one slot per regeneration. Two changes and you can't tell what fixed it.
5. If the plan changes: `python3 space/build.py && python3 space/massing.py`,
   then view 1, then the rest.

## Deliver like this

Numbered blocks, one per view, labelled with the wall or face and the
intended use, scene lock included in each so the block can be pasted alone.
No preamble inside the block.
