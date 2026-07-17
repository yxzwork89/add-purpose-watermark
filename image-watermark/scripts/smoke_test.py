#!/usr/bin/env python3
"""Smoke test for the watermark assistant script."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    print("Pillow is required for the smoke test: python -m pip install pillow", file=sys.stderr)
    sys.exit(2)


def load_watermark_module(script_path: Path):
    spec = spec_from_file_location("apply_watermark", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load apply_watermark.py")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def alpha_covariance(image: Image.Image) -> float:
    alpha = image.getchannel("A")
    pixels: list[tuple[int, int, int]] = []
    for y in range(alpha.height):
        for x in range(alpha.width):
            weight = alpha.getpixel((x, y))
            if weight:
                pixels.append((x, y, weight))
    total = sum(weight for _, _, weight in pixels)
    mean_x = sum(x * weight for x, _, weight in pixels) / total
    mean_y = sum(y * weight for _, y, weight in pixels) / total
    return sum((x - mean_x) * (y - mean_y) * weight for x, y, weight in pixels) / total


def verify_plugin_geometry(script_path: Path) -> None:
    module = load_watermark_module(script_path)
    options = module.WatermarkOptions(
        text="For test only",
        color=(107, 114, 128),
        opacity=60,
        size="medium",
        angle=-30,
        gap_x=40,
        gap_y=40,
        output_format="original",
        quality=None,
        suffix="watermark",
        output_dir=None,
        recursive=False,
    )
    layout = module.calculate_layout((960, 620), options)
    expected_base = min(max((960**2 + 620**2) ** 0.5 / (2**0.5), 620), 620 * 1.6)
    if layout.font_size != 28 or abs(layout.gap_x - expected_base * 0.4) > 0.01:
        raise AssertionError("Layout no longer matches the browser plug-in formula.")

    font = module.load_font(layout.font_size)
    tile = module.build_text_tile(
        ["For test only"],
        font,
        (107, 114, 128, 153),
        layout.line_height,
        options.angle,
    )
    if alpha_covariance(tile) >= 0:
        raise AssertionError("Default -30 degree watermark must rise from left to right.")


def create_sample(path: Path, image_format: str) -> None:
    image = Image.new("RGB", (960, 620), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 70, 890, 550), radius=20, fill="#FFFFFF", outline="#CBD5E1", width=4)
    draw.rectangle((110, 130, 350, 300), fill="#DBEAFE", outline="#3B82F6", width=3)
    draw.text((390, 140), "SAMPLE DOCUMENT", fill="#0F172A")
    draw.text((390, 190), "Name: Example User", fill="#334155")
    draw.text((390, 235), "ID: 000000000000000000", fill="#334155")
    draw.text((110, 390), "This is synthetic test data.", fill="#64748B")
    if image_format == "JPEG":
        image.save(path, format=image_format, quality=95)
    else:
        image.save(path, format=image_format)


def main() -> int:
    script_path = Path(__file__).with_name("apply_watermark.py")
    verify_plugin_geometry(script_path)
    with tempfile.TemporaryDirectory(prefix="image-watermark-") as temp_dir:
        temp_path = Path(temp_dir)
        input_path = temp_path / "sample.jpg"
        png_path = temp_path / "sample-extra.png"
        create_sample(input_path, "JPEG")
        create_sample(png_path, "PNG")
        command = [
            sys.executable,
            str(script_path),
            "--input",
            str(temp_path),
            "--text",
            "仅供测试使用\\nFor test only",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return result.returncode

        output_dir = temp_path / "watermarked"
        expected_outputs = [
            output_dir / "sample_watermark.jpg",
            output_dir / "sample-extra_watermark.png",
        ]
        for output_path in expected_outputs:
            if not output_path.exists():
                print(f"Expected output missing: {output_path}", file=sys.stderr)
                return 1

        before = Image.open(input_path).convert("RGB")
        after = Image.open(expected_outputs[0]).convert("RGB")
        diff = ImageChops.difference(before, after)
        if diff.getbbox() is None:
            print("Output image did not change.", file=sys.stderr)
            return 1

        with Image.open(input_path) as jpeg_before, Image.open(expected_outputs[0]) as jpeg_after:
            if jpeg_after.format != "JPEG" or jpeg_after.size != jpeg_before.size:
                print("JPEG format or dimensions were not preserved.", file=sys.stderr)
                return 1
            if jpeg_after.quantization != jpeg_before.quantization:
                print("JPEG quantization settings were not preserved.", file=sys.stderr)
                return 1

        with Image.open(png_path) as png_before, Image.open(expected_outputs[1]) as png_after:
            if png_after.format != "PNG" or png_after.size != png_before.size:
                print("PNG format or dimensions were not preserved.", file=sys.stderr)
                return 1

        print("Smoke test passed")
        for output_path in expected_outputs:
            print(output_path)
        return 0


if __name__ == "__main__":
    sys.exit(main())
