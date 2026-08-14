---
name: kora-shot-prompts
description: Write photorealistic studio product-photography prompts for kōra café drinks, ready to paste into ChatGPT (or any image model). Use when asked for images, photos, shots, or renders of kōra menu items — cold brew, matcha, juices, wellness shots, sodas, pastries — or for hero/Instagram/menu-board imagery for the café.
---

# kōra studio-shot prompts

Produces paste-ready prompts for photoreal beverage photography, locked to kōra's
brand. Output prompts, not images — the rendering happens in ChatGPT.

## Brand constants — never vary these

| | |
|---|---|
| Café | kōra, Kamla Nagar, Delhi. Opening 1 Nov 2026 |
| Positioning | clean ingredients, short lists, wellness, minimal packaging |
| Audience | urban Gen Z / millennials, yoga & gym crowd, working professionals |
| Green | `#2f4a35` deep forest — backdrops, props, never the drink itself |
| Paper | `#faf8f3` warm off-white |
| Cups | clear PET to-go cups, 12 oz and 16 oz, flat lid or dome lid |
| Mark | white square, thin black border, lowercase `ō` |
| Mood | calm, clean, unfussy. Not moody-dark, not bright-bubbly |

**Anti-brand — never generate these:** cluttered props, rustic burlap/hessian,
coffee beans scattered everywhere, latte art hearts, neon colours, plastic straws
in shot, busy café interiors behind the drink, hands holding the cup unless
specifically asked, text or lettering floating in the frame.

## The formula

Every prompt fills seven slots, written as flowing prose. Image models respond
to natural description, not comma-separated tags.

1. **Shot type** — always open with `A professional studio product photograph of…`
2. **Subject** — the drink, the vessel, what's visibly inside, in physical order
   (bottom layer up)
3. **Action** — the one thing happening: a pour mid-stream, a ripple, condensation
   beading, ice settling, powder falling. One only. Two reads as chaos.
4. **Light** — see the recipes below; this is what separates real from render
5. **Camera** — lens, aperture, height. `85mm` or `100mm macro`, `f/4`, and an
   explicit angle
6. **Surface & background** — what it stands on, what's behind, how far the
   background falls off
7. **Finish** — grade, grain, mood closer

## Lighting recipes — pick by drink family

The single biggest quality lever. Match the recipe to what the liquid does
with light.

**Translucent** (juices, sodas, shots, iced teas) — **backlight it.**
> lit from directly behind by a large softbox so the liquid glows from within,
> with a white bounce card at front-left lifting the shadows, and a narrow
> specular highlight running down the left edge of the glass

**Opaque** (milk drinks, matcha lattes, milk tea) — **side light, soft.**
> lit by a single large softbox at 45 degrees camera-left, feathered so the
> falloff is gentle, with a subtle rim light separating the cup from the
> background

**Dark** (espresso, cold brew, house blend) — **rim light for edge definition.**
> lit by a softbox above and slightly behind, raking across the surface to catch
> the crema, with two thin rim lights defining both edges of the cup against the
> darker background

**Layered** (strawberry matcha, butterfly soda) — **backlight plus side fill,**
so each stratum separates:
> strong backlight through the cup so the colour layers separate and glow
> distinctly, plus a soft fill from camera-left to hold detail in the milk band

## Camera by intent

| Use | Prompt fragment |
|---|---|
| Website hero | `85mm lens at f/2.8, shot at cup height, dead-on, generous negative space above` |
| Instagram square | `100mm macro at f/4, slight three-quarter angle, tight crop` |
| Menu board | `85mm at f/5.6, straight-on, even focus front to back, isolated on seamless` |
| Detail / texture | `100mm macro at f/2.8, focused on the condensation, background fully melted` |

## Surfaces that suit the brand

Honed pale limestone · warm microcement · pale oak end-grain · brushed
travertine · seamless paper in `#faf8f3`. Backdrop is a soft gradient falling
from `#faf8f3` to a muted sage, or flat `#2f4a35` for high contrast.

Keep props to a maximum of two, and only if they're in the drink: a halved lime,
a ginger root, three strawberries. Never coffee sacks or scattered beans.

## The logo — read this before promising a branded cup

Image models render small text and logos unreliably. The `ō` comes out as `o`,
`ō` with the bar detached, `6`, or invented lettering. **Do not** try to prompt
the mark onto the cup for anything final.

**The reliable workflow:**

1. Generate the cup **unbranded** — describe it as `a plain unbranded clear
   plastic cup with no text, labels or logos of any kind`
2. Composite the real mark on afterwards. The vector already exists in
   `gallery.html` — a white square, 1px black border, Georgia `ō` — and can be
   dropped over the render in Figma, Canva, Photoshop, or Keynote in a minute.

This gives a mark that is pixel-correct and identical across every image, which
is the whole point of a logo. Prompting it produces a different wrong glyph each
time.

If the user insists on prompting it, describe it as `a small white square label
with a thin black border on the front of the cup` and leave the letter out
entirely — a blank square composites cleanly later.

## Writing the prompt

- One paragraph, flowing prose, 60–110 words. Longer dilutes; shorter goes generic
- Name colours in plain words (`deep forest green`, `pale sage`), not hex — models
  don't read hex reliably. Keep hex in your notes for the compositing stage
- State what's absent: `no text, no logos, no hands, no clutter`
- Ask for `natural imperfections — a single drip on the rim, uneven ice`. Perfect
  reads as CGI
- Close with a grade: `soft natural colour grade, fine photographic grain,
  shallow depth of field, editorial food photography`

## Iterating

If a result misses, change **one** slot and regenerate:

| Problem | Fix |
|---|---|
| Looks like a 3D render | add `fine photographic grain, subtle sensor noise, natural imperfections` |
| Flat, lifeless liquid | wrong light recipe — switch to backlight |
| Cluttered | cut props to zero, add `minimal, isolated on seamless background` |
| Wrong cup | specify `clear PET plastic to-go cup with a flat lid, straight tapered sides` |
| Colours off-brand | name the backdrop colour explicitly and add `muted, desaturated palette` |
| Garbled lettering | you prompted a logo — remove it, composite instead |

## Deliver like this

Give the user a numbered, copy-paste block per shot. Label each with the menu
item and its intended use. No preamble inside the block — it goes straight into
ChatGPT.
