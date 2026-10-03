# kōra — kōracafe.com

Static site for kōra, a clean-ingredient café opening in Delhi,
1 November 2026. No build step: plain HTML, CSS and a little vanilla JS.

```
index.html    single page — hero, space, story, ethos, signatures, menu, visit
gallery.html  drink studies, linked from the signatures section
styles.css    brand palette + layout (phone rules sit under max-width:760px)
main.js       phone nav toggle; menu category tabs (WAI-ARIA tabs pattern)
img/          drink study SVGs
img/space/    concept renders of the café, 800px + full size, WebP + JPEG
og-image.jpg  link preview (WhatsApp, iMessage, socials) — storefront render
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

Cloudflare Workers Builds (project `k-racafe`) builds from GitHub:
<https://github.com/ProjectMira/k-racafe>. Push to `main` and it runs
`npx wrangler deploy`, which reads `wrangler.jsonc` and publishes the repo root
as static assets (`.assetsignore` keeps config files out). Keep
`wrangler.jsonc`: without it, newer Wrangler tries to auto-generate a config
mid-build and the build fails (as it did on 3 Oct 2026).

A push is not a deploy: check the commit's status on GitHub and load the
live site before calling it done.

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
- Real photography; the drink studies in `img/` are illustrations and the
  space images in `img/space/` are concept renders, labelled as such on the
  page. Swap in photos of the real site once a location is signed
