---
name: image-watermark
description: Add local text watermarks to sensitive document images such as ID cards, passport photos, business licenses, contracts, household registration pages, certificates, and other JPG/PNG/WebP files. Use when the user asks to add a purpose watermark like "仅供XX平台实名认证使用", batch-process local images or directories, customize watermark appearance, suggest common purpose watermark text, or draft GitHub/Xiaohongshu publishing copy. Apply immediately with defaults when the user only supplies images and text. For "自定义水印", "水印+自定义", or equivalent basic customization, collect text, color, opacity, and size while keeping angle and spacing at defaults. Only for "高级自定义", "高级设置", or explicit custom angle/spacing requests, additionally collect angle, horizontal spacing, and vertical spacing. Treat attributes already stated in the user's prompt as confirmed, ask only for missing applicable attributes, and request one final approval after showing the complete summary. Preserve source format and available quality settings automatically.
---

# Image Watermark

## Overview

Add repeated purpose text watermarks to local images using `scripts/apply_watermark.py`. Keep the standard path immediate, use four questions for basic customization, and reserve angle and spacing questions for advanced customization.

## Interaction Modes

### Standard Mode

- When the user provides image path(s) and watermark text without explicitly requesting custom mode, run the script immediately with the defaults.
- Treat the supplied text as the exact custom watermark text; do not replace it with a preset.
- Apply any explicitly supplied style overrides directly. Do not ask about unspecified settings.
- Apply the same text and settings to all images supplied in one request. Do not ask separately for each image.

### Basic Custom Mode

- Enter basic custom mode when the user asks for `自定义水印`, `水印+自定义`, `自定义配置`, `watermark + custom`, or an equivalent guided setup without requesting advanced controls.
- Read `references/watermark-options.md` and collect only these four items in order: watermark text, color, opacity, and size. Skip any item already stated in the user's prompt.
- Keep angle at `-30` and both spacing values at `40`. Do not ask about them in basic custom mode.

### Advanced Custom Mode

- Enter advanced custom mode only when the user explicitly asks for `高级自定义`, `高级设置`, `逐项设置全部参数`, custom angle, custom spacing, or an equivalent advanced setup.
- Read `references/watermark-options.md` and collect the four basic items first, then angle, horizontal spacing, and vertical spacing. Skip any item already stated in the user's prompt.

### Custom Mode Rules

- Extract all explicitly supplied configuration values from the initial prompt before asking questions. Treat them as confirmed for the current request.
- Ask only about missing applicable items, one at a time and in sequence. Offer the default and valid choices or range in each question.
- Do not separately reconfirm supplied watermark text or any other supplied attribute. Include every supplied value in the final configuration summary instead.
- Record `默认` as acceptance of that item's default, then continue to the next item.
- If no applicable items are missing, proceed directly to the final configuration summary.
- Do not run the script until every applicable item has a value and the user has approved the final configuration summary.
- Apply one confirmed text and visual configuration to every image in the same request. Reuse that configuration for additional images in the same conversation unless the user asks to change it; do not confirm settings separately for each image.

## Core Workflow

1. Confirm the user has provided local image path(s) and watermark text.
2. If image paths are missing, ask for the path to one image, multiple images, or a directory.
3. If text is missing but the user gave a scenario, suggest one concise purpose watermark and ask for confirmation before processing.
4. If text and scenario are both missing, ask for the intended usage. Use `仅供XX事项办理使用` only as a placeholder and tell the user to replace `XX`.
5. Select standard mode unless the user explicitly requested basic or advanced custom mode.
6. In standard mode, do not ask about color, size, opacity, angle, or spacing. Run with defaults plus any explicit overrides.
7. In basic custom mode, ask only for missing values among text, color, opacity, and size; use default angle and spacing.
8. In advanced custom mode, ask only for missing values among all seven visual items, including angle and both spacing values.
9. Preserve each source image's format, dimensions, and available encoding-quality settings. Do not ask about format or quality.
10. Choose a sensible writable output directory according to the active agent environment. Do not ask the user to choose one.
11. Name each output `原文件名_watermark.原扩展名` unless avoiding a collision requires a distinct path.
12. Return the absolute output file path(s), noting that originals were not overwritten and processing stayed local.

## Script Usage

Single image:

```bash
python scripts/apply_watermark.py \
  --input "/path/to/id-card.jpg" \
  --text "仅限XX平台实名认证使用"
```

Multiple inputs or a directory:

```bash
python scripts/apply_watermark.py \
  --input "/path/to/front.jpg" \
  --input "/path/to/back.jpg" \
  --text "仅供XX银行开户使用"
```

```bash
python scripts/apply_watermark.py \
  --input "/path/to/images" \
  --text "仅供租房备案登记使用"
```

Advanced options only when requested:

```bash
python scripts/apply_watermark.py \
  --input "/path/to/contract.jpg" \
  --text "仅供合同审核使用" \
  --size large \
  --opacity 50
```

## Defaults

Use these defaults unless the user asks otherwise:

- Color: `#6B7280`
- Opacity: `60`
- Size: `medium`
- Angle: `-30`
- Gap: `40` horizontal and vertical
- Format and quality: preserve each source image's original format and available encoding settings
- Output directory: let the active agent choose a sensible writable local directory; the script fallback is a sibling `watermarked/` directory
- Filename: append `_watermark` before the original extension

## References

- Read `references/watermark-options.md` when choosing or explaining presets, parameters, supported formats, watermark text suggestions, or running custom mode.
- Read `references/publishing-copy.md` when the user asks for GitHub README copy, Xiaohongshu copy, privacy wording, or promotional text.
- Read `references/xiaohongshu-skill-qa.md` when preparing Xiaohongshu Skill publication details or checking platform-specific notes.

## Failure Handling

- If Pillow is missing, tell the user the script needs Pillow and suggest `python -m pip install pillow`; do not install dependencies without confirmation.
- If a path does not exist, report the path and ask for a valid image path or directory.
- If no supported image files are found, say supported input formats are JPG/JPEG, PNG, WebP, BMP, and TIFF.
- If one file fails during a batch, continue processing the rest and summarize successes and failures.
- Do not upload user images, call online watermark APIs, delete originals, or overwrite original files.

## Copywriting Guardrails

When drafting copy, emphasize local processing, no server upload, purpose labeling, and reduced risk from sending unmarked images. Do not claim absolute theft prevention, legal protection, or security guarantees.
