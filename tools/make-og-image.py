"""Generate the social share image (assets/og-image.png, 1200x630).

Uses the site's own design tokens so the card matches the site. Re-run after
changing the headline or palette:

    python tools/make-og-image.py

Requires Pillow. System fonts are used because the site's webfonts are not
installed locally; the card is typographic, not a pixel copy of the page.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Design tokens (styles/tokens.css)
PAPER = "#f4f3ee"
PAPER_3 = "#e4e2d8"
INK = "#16181f"
INK_3 = "#63656c"
COBALT = "#2440ce"

W, H = 1200, 630
MARGIN = 84

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og-image.png"

FONTS = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    for candidate in (name, "segoeui.ttf", "arial.ttf"):
        path = FONTS / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


bold = lambda s: font("segoeuib.ttf", s)
semi = lambda s: font("seguisb.ttf", s)
mono = lambda s: font("consola.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Faint docket grid, matching the preview facade's 48px rhythm.
for x in range(0, W, 48):
    d.line([(x, 0), (x, H)], fill=PAPER_3, width=1)
for y in range(0, H, 48):
    d.line([(0, y), (W, y)], fill=PAPER_3, width=1)

# Wordmark
d.text((MARGIN, MARGIN - 18), "AK", font=bold(46), fill=INK)
ak_w = d.textlength("AK", font=bold(46))
d.text((MARGIN + ak_w, MARGIN - 18), ".", font=bold(46), fill=COBALT)

d.text(
    (MARGIN + ak_w + 34, MARGIN - 4),
    "ACHCHUTHAN KUMARANANTHA",
    font=mono(19),
    fill=INK_3,
)

# Cobalt rule — the site's accent device
d.rectangle([MARGIN, 202, MARGIN + 96, 206], fill=COBALT)

# Headline
d.text((MARGIN, 236), "Full-stack", font=bold(86), fill=INK)
d.text((MARGIN, 330), "product engineer", font=bold(86), fill=INK)

# Supporting line
d.text(
    (MARGIN, 456),
    "Commerce platforms, ordering systems, and business",
    font=semi(29),
    fill=INK_3,
)
d.text((MARGIN, 494), "software for real organizations.", font=semi(29), fill=INK_3)

# Footer meta
d.line([(MARGIN, 562), (W - MARGIN, 562)], fill=PAPER_3, width=2)
d.text((MARGIN, 580), "GTA, CANADA", font=mono(20), fill=INK_3)
label = "AK-HAZEL.VERCEL.APP"
d.text(
    (W - MARGIN - d.textlength(label, font=mono(20)), 580),
    label,
    font=mono(20),
    fill=COBALT,
)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.1f} KB)")
