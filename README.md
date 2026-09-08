# kōra — kōracafe.com

Static site for kōra, a clean-ingredient café opening in Delhi,
1 November 2026. No build step: plain HTML, CSS and a little vanilla JS.

```
index.html    single page — hero, story, ethos, signatures, menu, visit
gallery.html  drink studies, linked from the signatures section
styles.css    brand palette + layout
main.js       menu category tabs (WAI-ARIA tabs pattern)
img/          drink study SVGs
brand/        logo kit — svg, png, print, favicon, social; build.py regenerates it
fonts/        one subset woff2 (see Wordmark below)
robots.txt    / sitemap.xml
```

## Brand

| | |
|---|---|
| Mark | white square, hairline rule, black `ō` |
| Wordmark | `kōra` (Fraunces, with Georgia fallback) — see below |
| Green | `#2f4a35` — buttons, active tab, accents |
| Deep green | `#23381f` — footer |
| Paper | `#faf8f3` · Ink `#111111` |

### The macron

Fraunces' stock `latin-ext` subset on Google Fonts draws `ō` (U+014D) with the
macron sitting over the *following* letter, so the wordmark renders as "koṟa".
`fonts/fraunces-omacron.woff2` is a 2 KB single-codepoint subset of Fraunces
itself (pulled from the Google Fonts `text=` pipeline, which composes the glyph
correctly; SIL OFL, same as Fraunces). It is declared as its own family,
`"Kora Macron"`, sitting first in `--serif` and scoped to `unicode-range:
U+014D` — so it wins for that one character, every other character still comes
from the CDN, and the file is only downloaded on pages that render an `ō`.

Keep it first in the stack. Dropping it brings the misplaced macron back.

## Local preview

```bash
python3 -m http.server 4321
```

Then open http://localhost:4321. (Or use the `kora-site` config in
`.claude/launch.json`.)

## Deploy

Cloudflare Pages builds from GitHub: <https://github.com/ProjectMira/k-racafe>.
Push to `main` and the site redeploys automatically.

```bash
git push
```

Pages project settings — there is no build step, so **the whole repository
root is published as-is**. Anything committed here is public: business
documents stay out of the repo (see `.gitignore`), because
`Kora-documentation/Partners Document/` holds scans of the partners' Aadhaar
and PAN cards.

| Setting | Value |
|---|---|
| Framework preset | None |
| Build command | *(leave empty)* |
| Build output directory | `/` |
| Production branch | `main` |

First-time connection: Cloudflare dashboard → **Workers & Pages** → **Create** →
**Pages** → **Connect to Git** → pick `ProjectMira/k-racafe`.

## Domain

`kōracafe.com` is an IDN; its punycode form is `xn--kracafe-5lb.com`. Both
point at the same place — browsers show the pretty form, DNS uses the
punycode. Machine-readable fields in `index.html` (canonical, og:url,
sitemap) deliberately use punycode.

Registrar: GoDaddy. To move DNS to Cloudflare, change the nameservers at
GoDaddy from `ns69/ns70.domaincontrol.com` to the pair Cloudflare assigns.

## Still to fill in

- **Neighbourhood and street address.** Not settled. Six Kamla Nagar /
  Jawahar Nagar properties were shortlisted, none signed; the 11 Aug 2026
  notes then open up Civil Lines, Hauz Khas, Lodhi Garden and Sunder
  Nursery. The site says "Delhi" only until this is decided (`#visit`,
  `<title>`, meta description, JSON-LD, footer)
- Sourcing claims. Suppliers are shortlisted, not contracted — nothing
  about coffee origin, dairy or tea is published yet
- Opening hours
- Phone / email / Instagram — no contact details exist in the brand docs yet
- Prices — the menu is deliberately price-free for now
- Real photography; the drink studies in `img/` are illustrations, not photos
