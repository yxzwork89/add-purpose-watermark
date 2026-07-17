# Watermark Options

Use this reference when choosing watermark text, explaining defaults, or mapping user style requests to CLI parameters.

## Defaults

- Color: `#6B7280`
- Opacity: `60`
- Size: `medium`
- Angle: `-30`
- Gap: `--gap-x 40 --gap-y 40`
- Format and quality: preserve the source image's format, dimensions, and available encoding-quality settings
- Output directory: let the active agent choose; the script fallback is `watermarked/` next to the source
- Filename: `原文件名_watermark.原扩展名`

## Basic Custom Confirmation Sequence

Use this sequence for `自定义水印`, `水印+自定义`, `自定义配置`, or equivalent basic customization. First extract any values already stated in the user's prompt. Walk through the sequence in order, skip supplied values without reconfirming them, and ask one question at a time only for missing values.

1. If watermark text is missing, ask for it. Otherwise record the supplied text without a separate confirmation. When suggesting `仅供XX事项办理使用`, require the user to replace `XX`.
2. If color is missing, offer gray `#6B7280` (default), white `#FFFFFF`, black `#000000`, red `#DC2626`, blue `#2563EB`, yellow `#FACC15`, or a custom hex color.
3. If opacity is missing, offer `10`, `30`, `60` (default), `90`, or a custom integer from `0` to `100`.
4. If size is missing, offer `small`, `medium` (default), `large`, or `xlarge`.

After item 4, keep angle at `-30`, `gap-x` at `40`, and `gap-y` at `40`. Do not ask about these advanced items. Show a concise configuration summary and ask for final approval.

## Advanced Custom Confirmation Sequence

Use this sequence only for `高级自定义`, `高级设置`, `逐项设置全部参数`, explicit custom angle/spacing, or equivalent advanced customization. Collect items 1-4 from the basic sequence first, skipping supplied values, then continue:

5. If angle is missing, offer `0`, `-30` (default, rising from left to right), `30`, or a custom numeric angle.
6. If horizontal spacing (`gap-x`) is missing, offer `30`, `40` (default), `50`, `60`, or a custom integer from `15` to `70`.
7. If vertical spacing (`gap-y`) is missing, offer `30`, `40` (default), `50`, `60`, or a custom integer from `15` to `70`.

After item 7, show a concise configuration summary and ask for final approval.

For both custom modes, include all supplied and newly collected values in the final summary, then ask for one final approval. Apply the approved configuration to all images supplied in the same request. Reuse it for additional images in the same conversation unless the user asks to change it. Run `scripts/apply_watermark.py` only after approval. Do not combine several pending items into one question.

Do not ask about output format, quality, output directory, filename suffix, or recursive directory scanning. Preserve each image's source format and available quality settings, let the active agent choose the output directory, and append `_watermark` to the filename. Directory recursion means scanning nested subdirectories; it is unrelated to processing multiple explicitly supplied images.

## Supported Inputs

- Preferred: JPG/JPEG, PNG, WebP
- Also accepted: BMP, TIFF
- HEIC/HEIF and PDF are not part of the first version.

## Chinese Presets

- 通用办理：`仅供XX事项办理使用`
- 银行开户：`仅供XX银行开户使用`
- 银行贷款：`仅供XX银行贷款申请使用`
- 租房备案：`仅供租房备案登记使用`
- 平台实名：`仅限XX平台实名认证使用`
- 资格审核：`仅作报考资格审核使用`
- 人事备案：`仅供单位人事备案使用`

## English Presets

- General: `For XX matter only`
- Bank account: `For XX bank account opening only`
- Bank loan: `For XX bank loan application only`
- Rental filing: `For rental registration only`
- Platform verification: `For XX platform verification only`
- Exam review: `For exam eligibility review only`
- HR archive: `For HR department filing only`

## Style Mapping

- "颜色深一点": use a darker color such as `--color "#374151"` or increase opacity.
- "颜色浅一点": use a lighter color such as `--color "#9CA3AF"` or decrease opacity.
- "透明一点": lower opacity, commonly `--opacity 30` or `--opacity 40`.
- "明显一点": raise opacity, commonly `--opacity 70`, or use `--size large`.
- "文字大一点": `--size large`; "特别大": `--size xlarge`.
- "文字小一点": `--size small`.
- "不要斜着": `--angle 0`.
- "往右斜": use a positive angle such as `--angle 30`.
- "更密一点": reduce spacing, for example `--gap-x 25 --gap-y 25`.
- "稀疏一点": increase spacing, for example `--gap-x 55 --gap-y 55`.
- "保留 PNG": no override is needed because source format is preserved by default.

## Output Naming

Default:

```text
原文件名_watermark.原扩展名
```

Example:

```text
card-front.jpg -> card-front_watermark.jpg
```

The script never writes over the original input file because output names include `_watermark` and are written to an output directory.
