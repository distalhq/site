# site

Source for [distal.run](https://distal.run) and the Distal brand assets.

| Path | What it is |
|---|---|
| `site/` | The static landing page: HTML, CSS, fonts, the animated ASCII earthrise, favicons and share card. |
| `brand/` | The logo, favicon set and social images for GitHub, X and LinkedIn. `brand/build.py` rebuilds all of them from the two vector sources. |
| `wrangler.jsonc` | Cloudflare Workers static-assets config. |

## Rebuild the brand assets

Needs `rsvg-convert`, ImageMagick (`magick`) and Python with `fonttools`.

```bash
python3 brand/build.py
```

## Preview and deploy

```bash
python3 -m http.server 8765 --directory site
npx wrangler deploy
```

The Distal name, mark and wordmark are not licensed for reuse. The code is not yet under an open license; all rights are reserved until one is added. The fonts (Archivo Black, Manrope, IBM Plex Mono) are used under their own open licenses.
