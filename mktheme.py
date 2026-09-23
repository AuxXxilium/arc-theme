"""Draw the arc GRUB artwork from the logo.

Run from the repository root:  python mktheme.py
Needs Pillow. The PNGs it writes are committed, so this only runs when the
logo, the accent colour or the layout changes.

The layout is arx's, which is itself arc's banner with new artwork: the mark
on the left, a dashed rule running out from it to the right, and the same
mark small in the footer. arx draws two interlocking squares there; arc
draws its own logo, the red and grey triangles in artwork/arc_logo.png.

The logo's base rests on the rule's line. At banner size the base stroke is
about the rule's height, so the dashes read as the base carried on across
the banner rather than as a separate element beside it.

The red is moved to #d12b2b, the progress bar's fg_color and the menu's
selected_item_color in theme.txt, so the banner and the menu read as one
accent. The grey is the logo's own.

Why the edge handling: the source has hard red and grey fills, but the
antialiased pixels around them carry a stray light blue, not either fill.
Scaled down as-is, that blue becomes a cool fringe on every outline. So
each partly transparent pixel takes the colour of whichever fill it borders
and keeps only its alpha, which is the part of it that is right.
"""

import os
from PIL import Image, ImageFilter

SRC = os.path.join("artwork", "arc_logo.png")
OUT_DIR = "theme"

# The logo's two fills, as they appear in the source PNG.
SRC_RED = (255, 7, 0)
SRC_GREY = (77, 89, 109)

DST_RED = (209, 43, 43)
DST_GREY = SRC_GREY

# Banner and footer sizes, and where the offsets in theme.txt expect them.
LOADER_SIZE = (822, 180)
FOOTER_SIZE = (370, 24)

# The rule: 8px dashes 46px long on a 64px pitch, as in arx's banner. Its
# right end is arx's too; the left end follows the logo, RULE_GAP past it.
RULE_TOP = 154
RULE_HEIGHT = 8
RULE_DASH = 46
RULE_PITCH = 64
RULE_GAP = 26
RULE_RIGHT = 812

# The logo in the banner: its base on the rule's bottom edge.
LOGO_LEFT = 8
LOGO_HEIGHT = 140

FOOTER_LOGO_HEIGHT = 20


def clean(im):
    """Recolour the logo and give its fringe the colour of its fill."""
    im = im.convert("RGBA").crop(im.getchannel("A").getbbox())
    w, h = im.size
    px = im.load()

    red = Image.new("L", im.size, 0)
    rp = red.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][:3] == SRC_RED and px[x, y][3] == 255:
                rp[x, y] = 255
    # Far enough to reach every fringe pixel; the two shapes are further
    # apart than this, so the red never reaches the grey's edge.
    near_red = red.filter(ImageFilter.MaxFilter(9)).load()

    out = Image.new("RGBA", im.size)
    op = out.load()
    for y in range(h):
        for x in range(w):
            a = px[x, y][3]
            if a == 0:
                continue
            op[x, y] = (DST_RED if near_red[x, y] else DST_GREY) + (a,)
    return out


def scaled(logo, height):
    width = round(logo.width * height / logo.height)
    # Premultiplied, so transparent pixels do not bleed into the edges.
    return logo.convert("RGBa").resize((width, height), Image.LANCZOS).convert("RGBA")


def loader(logo):
    im = Image.new("RGBA", LOADER_SIZE)
    mark = scaled(logo, LOGO_HEIGHT)
    im.alpha_composite(mark, (LOGO_LEFT, RULE_TOP + RULE_HEIGHT - LOGO_HEIGHT))

    x = LOGO_LEFT + mark.width + RULE_GAP
    while x <= RULE_RIGHT:
        end = min(x + RULE_DASH, RULE_RIGHT + 1)
        im.paste(DST_RED + (255,), (x, RULE_TOP, end, RULE_TOP + RULE_HEIGHT))
        x += RULE_PITCH
    return im


def footer(logo):
    im = Image.new("RGBA", FOOTER_SIZE)
    mark = scaled(logo, FOOTER_LOGO_HEIGHT)
    im.alpha_composite(
        mark,
        ((FOOTER_SIZE[0] - mark.width) // 2, (FOOTER_SIZE[1] - mark.height) // 2),
    )
    return im


def main():
    logo = clean(Image.open(SRC))
    for name, im in (("arc_loader.png", loader(logo)), ("arc_footer.png", footer(logo))):
        dst = os.path.join(OUT_DIR, name)
        im.save(dst, optimize=True)
        print("%s  %dx%d" % (dst, im.width, im.height))


if __name__ == "__main__":
    main()
