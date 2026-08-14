# kōra — kōracafe.com

Static site for kōra, a clean-ingredient café opening in Delhi,
1 November 2026. No build step: plain HTML, CSS and a little vanilla JS.

```
index.html    single page — hero, ethos, menu, visit
styles.css    brand palette + layout
main.js       menu category tabs (WAI-ARIA tabs pattern)
robots.txt    / sitemap.xml
```

## Brand

| | |
|---|---|
| Mark | white square, hairline rule, black `ō` |
| Wordmark | `kōra` (Fraunces, with Georgia fallback) |
| Green | `#2f4a35` — buttons, active tab, accents |
| Deep green | `#23381f` — footer |
| Paper | `#faf8f3` · Ink `#111111` |

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

Pages project settings — there is no build step, so:

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
- Real photography; the site currently carries no images
