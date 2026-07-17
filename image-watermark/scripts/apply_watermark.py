#!/usr/bin/env python3
"""Apply repeated text watermarks to local images."""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, JpegImagePlugin
except ImportError:  # pragma: no cover - exercised only when Pillow is absent
    print(
        "Pillow is required. Install it with: python -m pip install pillow",
        file=sys.stderr,
    )
    sys.exit(2)


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
SIZE_RATIOS = {
    "small": 0.035,
    "medium": 0.045,
    "large": 0.058,
    "xlarge": 0.072,
}
MIN_FONT_SIZES = {
    "small": 8,
    "medium": 10,
    "large": 12,
    "xlarge": 14,
}
FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]


@dataclass(frozen=True)
class WatermarkOptions:
    text: str
    color: tuple[int, int, int]
    opacity: int
    size: str
    angle: float
    gap_x: int
    gap_y: int
    output_format: str
    quality: int | None
    suffix: str
    output_dir: Path | None
    recursive: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add local repeated text watermarks to image files.",
    )
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Image path or directory. Repeat for multiple inputs.",
    )
    parser.add_argument("--text", required=True, help="Watermark text. Use \\n for lines.")
    parser.add_argument("--output-dir", help="Directory for output files.")
    parser.add_argument("--color", default="#6B7280", help="Hex color, e.g. #6B7280.")
    parser.add_argument("--opacity", type=int, default=60, help="Opacity from 0 to 100.")
    parser.add_argument(
        "--size",
        default="medium",
        choices=sorted(SIZE_RATIOS),
        help="Relative text size.",
    )
    parser.add_argument("--angle", type=float, default=-30, help="Watermark angle in degrees.")
    parser.add_argument("--gap-x", type=int, default=40, help="Horizontal spacing scale, 15-70.")
    parser.add_argument("--gap-y", type=int, default=40, help="Vertical spacing scale, 15-70.")
    parser.add_argument(
        "--format",
        default="original",
        choices=["original", "jpg", "png"],
        help="Output format override. Defaults to preserving each source format.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=None,
        help="Optional JPEG/WebP quality override from 1 to 100.",
    )
    parser.add_argument(
        "--suffix",
        default="watermark",
        help="Filename suffix. Defaults to watermark.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively collect supported images from input directories.",
    )
    return parser.parse_args()


def parse_hex_color(value: str) -> tuple[int, int, int]:
    color = value.strip()
    if color.startswith("#"):
        color = color[1:]
    if len(color) == 3:
        color = "".join(char * 2 for char in color)
    if len(color) != 6:
        raise ValueError(f"Invalid hex color: {value}")
    try:
        return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise ValueError(f"Invalid hex color: {value}") from exc


def normalize_text(value: str) -> list[str]:
    text = value.replace("\\n", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Watermark text cannot be empty.")
    return lines


def validate_options(args: argparse.Namespace) -> WatermarkOptions:
    if not 0 <= args.opacity <= 100:
        raise ValueError("--opacity must be between 0 and 100.")
    if not 15 <= args.gap_x <= 70:
        raise ValueError("--gap-x must be between 15 and 70.")
    if not 15 <= args.gap_y <= 70:
        raise ValueError("--gap-y must be between 15 and 70.")
    if args.quality is not None and not 1 <= args.quality <= 100:
        raise ValueError("--quality must be between 1 and 100.")
    normalize_text(args.text)
    return WatermarkOptions(
        text=args.text,
        color=parse_hex_color(args.color),
        opacity=args.opacity,
        size=args.size,
        angle=args.angle,
        gap_x=args.gap_x,
        gap_y=args.gap_y,
        output_format=args.format,
        quality=args.quality,
        suffix=args.suffix,
        output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else None,
        recursive=args.recursive,
    )


def collect_images(inputs: Iterable[str], recursive: bool) -> tuple[list[Path], list[str]]:
    images: list[Path] = []
    errors: list[str] = []
    for raw_input in inputs:
        path = Path(raw_input).expanduser()
        if not path.exists():
            errors.append(f"Input path does not exist: {path}")
            continue
        if path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            for candidate in iterator:
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    images.append(candidate.resolve())
            continue
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            images.append(path.resolve())
        else:
            errors.append(f"Unsupported image file: {path}")
    unique_images = list(dict.fromkeys(images))
    return unique_images, errors


def load_font(font_size: int) -> ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        font_path = Path(candidate)
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), font_size)
            except OSError:
                continue
    try:
        return ImageFont.truetype("DejaVuSans.ttf", font_size)
    except OSError:
        return ImageFont.load_default()


@dataclass(frozen=True)
class WatermarkLayout:
    font_size: int
    line_height: int
    gap_x: float
    gap_y: float
    extent: int


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def js_round(value: float) -> int:
    """Match JavaScript Math.round for the non-negative layout values used here."""
    return math.floor(value + 0.5)


def calculate_layout(image_size: tuple[int, int], options: WatermarkOptions) -> WatermarkLayout:
    """Mirror the browser plug-in's canvas layout calculations."""
    width, height = image_size
    short_edge = max(1, min(width, height))
    normalized_diagonal = math.hypot(width, height) / math.sqrt(2)
    base = clamp(normalized_diagonal, short_edge, short_edge * 1.6)
    size_floor = max(js_round(clamp(short_edge * 0.025, 8, 16)), MIN_FONT_SIZES[options.size])
    font_size = max(js_round(short_edge * SIZE_RATIOS[options.size]), size_floor)
    return WatermarkLayout(
        font_size=font_size,
        line_height=js_round(font_size * 1.35),
        gap_x=base * clamp(options.gap_x, 15, 70) / 100,
        gap_y=base * clamp(options.gap_y, 15, 70) / 100,
        extent=max(width, height),
    )


def build_text_tile(
    lines: list[str],
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    line_height: int,
    plugin_angle: float,
) -> Image.Image:
    """Render one centered block using the plug-in's canvas angle convention."""
    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    widths = [measure.textlength(line, font=font) for line in lines]
    block_width = max(1, math.ceil(max(widths)))
    block_height = max(1, line_height * len(lines))
    padding = max(4, line_height)
    tile = Image.new(
        "RGBA",
        (block_width + padding * 2, block_height + padding * 2),
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(tile)
    center_x = tile.width / 2
    first_line_y = tile.height / 2 - (block_height - line_height) / 2
    for index, line in enumerate(lines):
        draw.text(
            (center_x, first_line_y + index * line_height),
            line,
            font=font,
            fill=fill,
            anchor="mm",
        )

    # Canvas uses a downward-positive Y axis. Pillow's visual rotation uses the
    # opposite sign, so a plug-in angle of -30 degrees becomes +30 degrees here.
    return tile.rotate(-plugin_angle, resample=Image.Resampling.BICUBIC, expand=True)


def build_watermark_layer(image_size: tuple[int, int], options: WatermarkOptions) -> Image.Image:
    width, height = image_size
    layout = calculate_layout(image_size, options)
    font = load_font(layout.font_size)
    lines = normalize_text(options.text)
    alpha = round(255 * options.opacity / 100)
    fill = (*options.color, alpha)
    tile = build_text_tile(lines, font, fill, layout.line_height, options.angle)
    layer = Image.new("RGBA", image_size, (0, 0, 0, 0))

    row = 0
    y = -float(layout.extent)
    while y <= height + layout.extent:
        offset_x = layout.gap_x / 2 if row % 2 else 0
        x = -float(layout.extent) - offset_x
        while x <= width + layout.extent:
            position = (round(x - tile.width / 2), round(y - tile.height / 2))
            layer.alpha_composite(tile, dest=position)
            x += layout.gap_x
        y += layout.gap_y
        row += 1
    return layer


def output_path_for(input_path: Path, options: WatermarkOptions, extension: str) -> Path:
    output_dir = options.output_dir or input_path.parent / "watermarked"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{input_path.stem}_{options.suffix}{extension}"


def output_format_for(input_path: Path, source_format: str, override: str) -> tuple[str, str]:
    if override == "jpg":
        return "JPEG", ".jpg"
    if override == "png":
        return "PNG", ".png"

    normalized = source_format.upper()
    if normalized not in {"JPEG", "PNG", "WEBP", "BMP", "TIFF"}:
        raise ValueError(f"Cannot preserve unsupported source format: {source_format}")
    return normalized, input_path.suffix.lower()


def flatten_to_rgb(composed: Image.Image) -> Image.Image:
    background = Image.new("RGB", composed.size, (255, 255, 255))
    background.paste(composed.convert("RGB"), mask=composed.getchannel("A"))
    return background


def apply_watermark(input_path: Path, options: WatermarkOptions) -> Path:
    with Image.open(input_path) as opened:
        source_format = opened.format or input_path.suffix.lstrip(".")
        jpeg_quantization = getattr(opened, "quantization", None)
        jpeg_subsampling = JpegImagePlugin.get_sampling(opened) if source_format == "JPEG" else None
        source_compression = opened.info.get("compression")
        source_lossless = bool(opened.info.get("lossless", False))
        image = ImageOps.exif_transpose(opened)
        base = image.convert("RGBA")
    overlay = build_watermark_layer(base.size, options)
    composed = Image.alpha_composite(base, overlay)
    output_format, extension = output_format_for(input_path, source_format, options.output_format)
    output_path = output_path_for(input_path, options, extension)

    if output_format == "JPEG":
        save_options: dict[str, object] = {"optimize": True}
        if options.quality is not None:
            save_options["quality"] = options.quality
        elif jpeg_quantization:
            save_options["qtables"] = jpeg_quantization
            if jpeg_subsampling in {0, 1, 2}:
                save_options["subsampling"] = jpeg_subsampling
        else:
            save_options["quality"] = 95
        flatten_to_rgb(composed).save(output_path, format="JPEG", **save_options)
    elif output_format == "PNG":
        composed.save(output_path, format="PNG", optimize=True)
    elif output_format == "WEBP":
        webp_options: dict[str, object] = {"method": 6}
        if source_lossless and options.quality is None:
            webp_options["lossless"] = True
        else:
            webp_options["quality"] = options.quality or 95
        composed.save(output_path, format="WEBP", **webp_options)
    elif output_format == "TIFF":
        tiff_options = {"compression": source_compression} if source_compression else {}
        composed.save(output_path, format="TIFF", **tiff_options)
    else:
        flatten_to_rgb(composed).save(output_path, format="BMP")
    return output_path.resolve()


def main() -> int:
    args = parse_args()
    try:
        options = validate_options(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    images, input_errors = collect_images(args.input, options.recursive)
    if input_errors:
        for error in input_errors:
            print(f"Warning: {error}", file=sys.stderr)
    if not images:
        print("Error: no supported image files found.", file=sys.stderr)
        return 1

    successes: list[Path] = []
    failures: list[tuple[Path, str]] = []
    for image_path in images:
        try:
            successes.append(apply_watermark(image_path, options))
        except Exception as exc:  # noqa: BLE001 - continue batch processing with a summary
            failures.append((image_path, str(exc)))

    print(f"Processed: {len(successes)} succeeded, {len(failures)} failed")
    for output_path in successes:
        print(output_path)
    if failures:
        print("Failures:", file=sys.stderr)
        for path, message in failures:
            print(f"- {path}: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
