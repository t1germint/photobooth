from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TARGET_W = 1800
TARGET_H = 1200
BAR_HEIGHT = 160
BAR_Y = TARGET_H - BAR_HEIGHT
TEXT_COLOR = "#111111"
TEXT_SIZE = 76
LEFT_PAD = 90
RIGHT_PAD = 90
LOGO_H = 110


def _load_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size=size)
    try:
        return ImageFont.truetype("arialbd.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def _cover_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    tgt_ratio = target_w / target_h

    if src_ratio > tgt_ratio:
        new_h = src_h
        new_w = int(new_h * tgt_ratio)
        x0 = (src_w - new_w) // 2
        y0 = 0
    else:
        new_w = src_w
        new_h = int(new_w / tgt_ratio)
        x0 = 0
        y0 = (src_h - new_h) // 2

    cropped = img.crop((x0, y0, x0 + new_w, y0 + new_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def render_final(raw_path: Path, final_path: Path, mode_name: str, logo_path: Path, font_path: Path) -> Path:
    with Image.open(raw_path).convert("RGB") as raw:
        canvas = _cover_resize(raw, TARGET_W, TARGET_H)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, BAR_Y, TARGET_W, TARGET_H), fill="white")

    font_size = TEXT_SIZE
    font = _load_font(font_path, font_size)
    max_text_width = TARGET_W - LEFT_PAD - RIGHT_PAD - 350
    while True:
        bbox = draw.textbbox((0, 0), mode_name, font=font)
        text_w = bbox[2] - bbox[0]
        if text_w <= max_text_width or font_size <= 34:
            break
        font_size -= 2
        font = _load_font(font_path, font_size)

    text_h = bbox[3] - bbox[1]
    text_x = LEFT_PAD
    text_y = BAR_Y + (BAR_HEIGHT - text_h) // 2 - 3
    draw.text((text_x, text_y), mode_name, fill=TEXT_COLOR, font=font)

    if logo_path.exists():
        with Image.open(logo_path).convert("RGBA") as logo:
            ratio = LOGO_H / logo.height
            logo_w = int(logo.width * ratio)
            logo_resized = logo.resize((logo_w, LOGO_H), Image.Resampling.LANCZOS)
            logo_x = TARGET_W - RIGHT_PAD - logo_w
            logo_y = BAR_Y + (BAR_HEIGHT - LOGO_H) // 2
            canvas.paste(logo_resized, (logo_x, logo_y), logo_resized)

    final_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(final_path, format="JPEG", quality=95)
    return final_path
