"""Meme Sprint: AI Agents Ship Games.

Draws a two-panel meme, 1024x1024, to /output/entry.png.

Panel 1 (ME): a human at a laptop asks for one tiny fix.
Panel 2 (MY AI AGENT, 40 SECONDS LATER): the agent has rebuilt the whole
game as a roguelike with a battle pass.

Deterministic: no network, no clock, no randomness. The only font is
bundled in this repo (fonts/DejaVuSans-Bold.ttf) and loaded by path.
"""

import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = HERE / "fonts" / "DejaVuSans-Bold.ttf"

W, H = 1024, 1024
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_bubble(draw, box, tail, lines, fnt, line_h):
    """White rounded speech bubble with a black outline and a tail."""
    draw.polygon(tail, fill=WHITE, outline=BLACK)
    draw.rounded_rectangle(box, radius=22, fill=WHITE, outline=BLACK, width=4)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    total_h = line_h * len(lines)
    y = y0 + (y1 - y0 - total_h) // 2
    for line in lines:
        draw.text((cx, y), line, font=fnt, fill=BLACK, anchor="ma")
        y += line_h


def draw_chip(draw, x, y, text, size):
    """Black label chip; returns its right edge."""
    fnt = font(size)
    tw = draw.textlength(text, font=fnt)
    pad = 24
    box = [x, y, x + int(tw) + pad * 2, y + size + 26]
    draw.rounded_rectangle(box, radius=12, fill=BLACK)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2),
              text, font=fnt, fill=WHITE, anchor="mm")
    return box[2]


def draw_laptop(draw, x, y, screen_w=96, screen_h=72):
    """A laptop on a desk: base + screen showing a tiny game scene."""
    base = [x, y, x + screen_w + 14, y + 14]
    screen = [x + 7, y - screen_h, x + 7 + screen_w, y]
    draw.rectangle(base, fill=(60, 60, 60), outline=BLACK, width=3)
    draw.rectangle(screen, fill=(30, 42, 50), outline=BLACK, width=3)
    # tiny game inside the screen
    sx0, sy0, sx1, sy1 = screen
    draw.rectangle([sx0 + 3, sy0 + 3, sx1 - 3, sy0 + 44],
                   fill=(126, 200, 247))
    draw.rectangle([sx0 + 3, sy0 + 44, sx1 - 3, sy1 - 3],
                   fill=(88, 179, 104))
    draw.rectangle([sx0 + 34, sy0 + 28, sx0 + 48, sy0 + 44],
                   fill=(255, 214, 64), outline=BLACK, width=2)
    draw.ellipse([sx0 + 66, sy0 + 16, sx0 + 78, sy0 + 28],
                 fill=(255, 214, 64), outline=BLACK, width=2)
    return screen


def draw_human(draw):
    """Stick-figure human, bust behind a desk, typing at a laptop."""
    # head
    draw.ellipse([228, 318, 312, 402], outline=BLACK, width=6)
    # shoulders
    draw.arc([196, 386, 344, 478], start=180, end=360, fill=BLACK, width=8)
    # arm reaching to the laptop
    draw.line([(330, 432), (392, 420)], fill=BLACK, width=8)
    # desk
    draw.rectangle([120, 440, 430, 462], fill=(150, 110, 70),
                   outline=BLACK, width=3)
    draw.line([(140, 462), (140, 496)], fill=BLACK, width=6)
    draw.line([(410, 462), (410, 496)], fill=BLACK, width=6)
    draw_laptop(draw, 330, 440)


def draw_robot(draw):
    """Friendly robot bust behind a desk, shipping at full speed."""
    # antenna
    draw.line([(280, 820), (280, 788)], fill=BLACK, width=6)
    draw.ellipse([268, 772, 292, 796], fill=(220, 60, 60),
                 outline=BLACK, width=3)
    # head
    draw.rounded_rectangle([220, 820, 340, 940], radius=26,
                           fill=(184, 196, 204), outline=BLACK, width=4)
    # eyes
    draw.ellipse([246, 858, 272, 884], fill=(60, 200, 90),
                 outline=BLACK, width=3)
    draw.ellipse([288, 858, 314, 884], fill=(60, 200, 90),
                 outline=BLACK, width=3)
    # smile
    draw.arc([252, 888, 308, 926], start=15, end=165, fill=BLACK, width=4)
    # body
    draw.rounded_rectangle([214, 946, 346, 1024], radius=18,
                           fill=(184, 196, 204), outline=BLACK, width=4)
    # arm to the laptop
    draw.line([(340, 978), (452, 946)], fill=BLACK, width=8)
    # desk
    draw.rectangle([90, 952, 560, 976], fill=(150, 110, 70),
                   outline=BLACK, width=3)
    draw.line([(110, 976), (110, 1024)], fill=BLACK, width=6)
    draw.line([(540, 976), (540, 1024)], fill=BLACK, width=6)
    screen = draw_laptop(draw, 443, 952)
    # the agent's version counter on the laptop screen
    small = font(22)
    draw.text((screen[2] - 8, screen[3] - 6), "v47",
              font=small, fill=WHITE, anchor="rs")


def draw_confetti(draw):
    """Fixed confetti pieces (no randomness) around panel 2."""
    pieces = [
        (60, 600, (230, 60, 60)), (120, 660, (255, 200, 40)),
        (70, 740, (60, 120, 230)), (150, 800, (230, 60, 180)),
        (60, 880, (60, 200, 90)), (140, 920, (255, 140, 40)),
        (380, 620, (60, 120, 230)),
        (620, 940, (230, 60, 60)), (700, 900, (255, 200, 40)),
        (800, 960, (60, 120, 230)), (900, 900, (230, 60, 180)),
        (960, 980, (60, 200, 90)), (660, 1000, (255, 140, 40)),
        (920, 600, (60, 200, 90)), (980, 700, (255, 200, 40)),
        (40, 1000, (60, 120, 230)), (180, 990, (230, 60, 60)),
    ]
    for x, y, color in pieces:
        draw.rectangle([x, y, x + 16, y + 10], fill=color)


def main():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # ---- panel 1: ME -------------------------------------------------
    draw.rectangle([0, 0, W, 496], fill=(239, 239, 239))
    draw_chip(draw, 28, 24, "ME", 46)
    bubble_font = font(56)
    lines1 = wrap(draw, "just fix the jump button", bubble_font, 500)
    draw_bubble(draw, [430, 44, 988, 236],
                [(500, 236), (440, 300), (570, 236)],
                lines1, bubble_font, 72)
    draw_human(draw)

    # divider
    draw.rectangle([0, 496, W, 508], fill=BLACK)

    # ---- panel 2: MY AI AGENT, 40 SECONDS LATER ----------------------
    draw.rectangle([0, 508, W, H], fill=(221, 243, 213))
    draw_chip(draw, 28, 532, "MY AI AGENT \u00b7 40 SECONDS LATER", 38)
    draw_confetti(draw)
    lines2 = ["done. it's a", "roguelike now.", "with a battle pass."]
    bubble_font2 = font(48)
    draw_bubble(draw, [400, 600, 988, 856],
                [(480, 856), (420, 890), (550, 856)],
                lines2, bubble_font2, 62)
    draw_robot(draw)

    os.makedirs("/output", exist_ok=True)
    out = "/output/entry.png"
    img.save(out, format="PNG")
    data = Path(out).read_bytes()
    print("wrote", out, len(data), "bytes",
          img.size[0], "x", img.size[1],
          "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
