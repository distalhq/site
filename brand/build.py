#!/usr/bin/env python3
"""Builds every distal brand asset from the two vector sources below.

The mark and wordmark paths are the ones published at distal.run (angular "d"
mark + outlined letters "istal"). Nothing here is redrawn.

Needs: rsvg-convert, magick (ImageMagick). Run: python3 brand/build.py
"""
import os, shutil, subprocess, textwrap, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "..", "site", "fonts")
OUT = ROOT

INK, VERM, CREAM, WHITE = "#29232a", "#f65c3b", "#f2efdd", "#faf7ed"

# --- recovered vector sources -------------------------------------------------
MARK_D = "M235 0V254L171 315H54L0 264V189L97 115H165V55Z M61 177H165V252H61Z"  # 235 x 315
MARK_W, MARK_H = 235, 315
LETTERS_D = (
    "M463 86H492V117H463Z M463 140H492V276H463Z "
    "M623 181H596C593 169 584 164 569 164C553 164 542 170 542 181C542 191 550 196 571 200L588 203"
    "C614 208 626 222 626 242C626 265 605 278 572 278C539 278 516 263 513 238H542C544 250 554 254 572 254"
    "C589 254 599 249 599 240C599 230 590 226 572 223L552 219C526 214 513 202 513 181C513 155 536 138 568 138"
    "C598 138 620 154 623 181Z "
    "M661 99H690V140H720V168H690V238C690 245 693 248 701 248H720V276H700C674 276 661 264 661 239V168H638V140H661Z "
    "M844 140H872V276H844V259C833 271 818 277 801 277C761 277 733 248 733 208C733 168 762 139 802 139"
    "C819 139 834 145 844 157Z "
    "M844 208C844 185.08 825.42 166.5 802.5 166.5C779.58 166.5 761 185.08 761 208C761 230.92 779.58 249.5 802.5 249.5"
    "C825.42 249.5 844 230.92 844 208Z "
    "M897 86H926V276H897Z"
)
# wordmark lives in viewBox "0 84 634 196": mark scaled to .6032 at (0,86), letters shifted -292
WM_X, WM_Y, WM_W, WM_H = 0, 84, 634, 196


def mark_svg(color, size=None):
    s = f' width="{size}" height="{round(size*MARK_H/MARK_W)}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MARK_W} {MARK_H}"{s} role="img" aria-label="Distal">'
            f'<title>Distal</title><path fill="{color}" fill-rule="evenodd" d="{MARK_D}"/></svg>\n')


def wordmark_inner(color):
    return (f'<path transform="translate(0 86) scale(0.6031746)" fill="{color}" fill-rule="evenodd" d="{MARK_D}"/>'
            f'<path transform="translate(-292 0)" fill="{color}" fill-rule="evenodd" d="{LETTERS_D}"/>')


def logo_svg(color, pad=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{WM_X-pad} {WM_Y-pad} {WM_W+2*pad} {WM_H+2*pad}" role="img" aria-label="Distal">'
            f'<title>Distal</title>{wordmark_inner(color)}</svg>\n')


def place_mark(color, cx, cy, height):
    s = height / MARK_H
    x, y = cx - MARK_W * s / 2, cy - height / 2
    return f'<path transform="translate({x:.3f} {y:.3f}) scale({s:.5f})" fill="{color}" fill-rule="evenodd" d="{MARK_D}"/>'


def place_logo(color, x, cy, height):
    """Wordmark with left edge x, vertically centred on cy, given cap height (mark height)."""
    s = height / (WM_H - 2)  # visual height of wordmark ~ 190
    # wordmark visual box: y from 86 to 278 (192 tall), x 0..634
    vis_h = 192
    s = height / vis_h
    return f'<g transform="translate({x:.2f} {cy - height/2:.2f}) scale({s:.5f}) translate(0 -86)">{wordmark_inner(color)}</g>', 634 * s


def square(size, bg, fg, mark_ratio, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{bg}"{r}/>{place_mark(fg, size/2, size/2, size*mark_ratio)}</svg>\n')



def text_path(text, color, x, baseline, size, tracking=0.0):
    """Outline text with Archivo Black so no renderer needs the font installed."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    f = TTFont(os.path.join(FONTS, "ArchivoBlack.ttf"))
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    sc = size / f["head"].unitsPerEm
    pen, cx = SVGPathPen(gs), x
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, baseline)))
        cx += hmtx[g][0] * sc + tracking * size
    return f'<path fill="{color}" d="{pen.getCommands()}"/>'

# --- helpers --------------------------------------------------------------------
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def fontconf():
    d = tempfile.mkdtemp()
    conf = os.path.join(d, "fonts.conf")
    open(conf, "w").write(
        f'<?xml version="1.0"?><fontconfig><dir>{os.path.abspath(FONTS)}</dir>'
        f'<cachedir>{d}/cache</cachedir></fontconfig>')
    return conf


ENV = dict(os.environ, FONTCONFIG_FILE=fontconf())


def png(svg_path, png_path, width=None, height=None):
    cmd = ["rsvg-convert", "-o", png_path]
    if width:
        cmd += ["-w", str(width)]
    if height:
        cmd += ["-h", str(height)]
    subprocess.run(cmd + [svg_path], check=True, env=ENV)


def make_png(name_svg, svg_text, out_png, width=None, height=None):
    src = os.path.join(ROOT, "src", name_svg)
    w(src, svg_text)
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    png(src, out_png, width, height)


def main():
    # 1. marks and logos (vector, 3 colourways) ---------------------------------
    for name, c in (("ink", INK), ("vermilion", VERM), ("cream", CREAM)):
        w(f"{OUT}/logo/distal-mark-{name}.svg", mark_svg(c))
        w(f"{OUT}/logo/distal-logo-{name}.svg", logo_svg(c, pad=0))
    for name, c in (("ink", INK), ("cream", CREAM)):
        png(f"{OUT}/logo/distal-logo-{name}.svg", f"{OUT}/logo/distal-logo-{name}.png", width=1600)
        png(f"{OUT}/logo/distal-mark-{name}.svg", f"{OUT}/logo/distal-mark-{name}.png", height=1024)

    # 2. favicon set ------------------------------------------------------------
    fav = f"{OUT}/favicon"
    os.makedirs(fav, exist_ok=True)
    w(f"{fav}/favicon.svg", square(32, VERM, INK, 0.66, rx=6))
    for s in (16, 32, 48):
        png(f"{fav}/favicon.svg", f"{fav}/favicon-{s}.png", width=s, height=s)
    subprocess.run(["magick", f"{fav}/favicon-16.png", f"{fav}/favicon-32.png", f"{fav}/favicon-48.png",
                    f"{fav}/favicon.ico"], check=True)
    make_png("apple-touch-icon.svg", square(180, VERM, INK, 0.62), f"{fav}/apple-touch-icon.png", 180, 180)
    make_png("icon-192.svg", square(192, VERM, INK, 0.62), f"{fav}/icon-192.png", 192, 192)
    make_png("icon-512.svg", square(512, VERM, INK, 0.62), f"{fav}/icon-512.png", 512, 512)
    # maskable: mark inside the central 60% safe zone
    make_png("icon-maskable-512.svg", square(512, VERM, INK, 0.46), f"{fav}/icon-maskable-512.png", 512, 512)
    w(f"{fav}/safari-pinned-tab.svg",
      f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path transform="translate(2.7 1) scale(0.0444)" '
      f'fill="#000" fill-rule="evenodd" d="{MARK_D}"/></svg>\n')
    w(f"{fav}/site.webmanifest", textwrap.dedent("""\
        {
          "id": "/",
          "name": "Distal",
          "short_name": "Distal",
          "lang": "en",
          "start_url": "/",
          "scope": "/",
          "display": "browser",
          "theme_color": "#f65c3b",
          "background_color": "#f2efdd",
          "icons": [
            { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
            { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
            { "src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
          ]
        }
        """))

    # 3. profile images (square; mark stays inside the circle crop) --------------
    prof = {"github/github-org-avatar-500": 500, "x/x-profile-400": 400, "linkedin/linkedin-logo-400": 400,
            "linkedin/linkedin-logo-300": 300}
    for path, s in prof.items():
        make_png(os.path.basename(path) + ".svg", square(s, VERM, INK, 0.50), f"{OUT}/social/{path}.png", s, s)
    # dark alternate
    make_png("avatar-dark-500.svg", square(500, INK, VERM, 0.50), f"{OUT}/social/alt/avatar-dark-500.png", 500, 500)
    make_png("avatar-cream-500.svg", square(500, CREAM, INK, 0.50), f"{OUT}/social/alt/avatar-cream-500.png", 500, 500)

    # 4. banners and cards --------------------------------------------------------
    def banner(W, H, x_logo, logo_h, tag, tag_size, fname_svg, out_png, gap=None, vcenter=None):
        gap = gap if gap is not None else logo_h * 0.4
        cy = vcenter if vcenter is not None else H / 2
        cap = tag_size * 0.7  # Archivo Black cap height ~0.7 em
        total = logo_h + gap + cap
        top = cy - total / 2
        group, _ = place_logo(INK, x_logo, top + logo_h / 2, logo_h)
        body = group + text_path(tag, INK, x_logo, top + logo_h + gap + cap, tag_size, tracking=0.04)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
               f'<rect width="{W}" height="{H}" fill="{VERM}"/>{body}</svg>\n')
        make_png(fname_svg, svg, out_png, W, H)

    # GitHub social preview 1280x640 (also used as the site share card at 1200x630)
    banner(1280, 640, 110, 150, "ONE CHIP BREAKS. YOUR KEYS DON’T.", 40, "github-social-preview.svg",
           f"{OUT}/social/github/github-social-preview-1280x640.png", gap=60)
    banner(1200, 630, 100, 140, "ONE CHIP BREAKS. YOUR KEYS DON’T.", 38, "og.svg", f"{OUT}/og.png", gap=56)
    # X header 1500x500; content right of the avatar overlap, inside mobile crop
    banner(1500, 500, 470, 110, "ONE CHIP BREAKS. YOUR KEYS DON’T.", 32, "x-header.svg",
           f"{OUT}/social/x/x-header-1500x500.png", gap=44, vcenter=235)
    # LinkedIn company cover 1128x191 (logo overlaps lower-left, keep content right of x=300)
    banner(1128, 191, 330, 62, "ONE CHIP BREAKS. YOUR KEYS DON’T.", 20, "linkedin-cover.svg",
           f"{OUT}/social/linkedin/linkedin-cover-1128x191.png", gap=22, vcenter=86)

    # 5. copy site-facing files -----------------------------------------------------
    site = os.path.join(ROOT, "..", "site")
    os.makedirs(site, exist_ok=True)
    for f in ("favicon.ico", "favicon.svg", "favicon-16.png", "favicon-32.png", "favicon-48.png", "apple-touch-icon.png",
              "icon-192.png", "icon-512.png", "icon-maskable-512.png", "safari-pinned-tab.svg", "site.webmanifest"):
        shutil.copy(f"{fav}/{f}", f"{site}/{f}")
    shutil.copy(f"{OUT}/og.png", f"{site}/og.png")
    shutil.copy(f"{OUT}/logo/distal-logo-ink.svg", f"{site}/distal-logo.svg")
    print("brand assets built")


if __name__ == "__main__":
    main()
