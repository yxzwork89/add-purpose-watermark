# Publishing Copy

Use this reference when drafting GitHub README sections, Xiaohongshu posts, privacy blurbs, and release copy.

## Positioning

图片水印 / Image Watermark helps users add purpose text watermarks to local document images before submitting them to banks, platforms, HR teams, rental filing systems, exam reviews, or similar workflows.

Emphasize:

- Local image processing
- No server upload
- Purpose labels such as `仅限XX平台实名认证使用`
- Batch processing
- Preserve each source image's format and available encoding-quality settings
- Originals are not overwritten

Do not claim:

- Absolute anti-theft protection
- Legal protection guarantees
- Browser upload injection in the Skill version
- Long-term image storage or cloud sync

## GitHub README Starter

````markdown
# 图片水印 / Image Watermark

本地给身份证、证件照、营业执照、合同、户口本、证书等图片添加用途文字水印。适合在提交敏感材料前标注“仅供某用途使用”，降低裸传图片的风险。

## Features

- 本地处理图片，不上传服务器
- 支持 JPG、PNG、WebP、BMP、TIFF 输入
- 支持单图、多图和目录批量处理
- 默认灰色半透明斜向平铺水印
- 支持普通自定义（颜色、透明度、字号）和高级自定义（角度、间距）
- 保持原图格式和尺寸，输出文件追加 `_watermark`，不覆盖原图

## Example

```bash
python image-watermark/scripts/apply_watermark.py \
  --input "/path/to/id-card.jpg" \
  --text "仅限XX平台实名认证使用"
```

## Privacy

图片只在本机读取和写入。脚本不调用在线水印 API，也不会主动上传用户图片。
````

## Xiaohongshu Copy

Title ideas:

- 上传证件前，先给图片加一句用途水印
- 身份证/营业执照本地加水印小工具
- 敏感材料别裸传：本地生成用途水印

Body:

```text
做了一个“图片水印”Skill：给身份证、证件照、营业执照、合同等图片添加用途水印，比如“仅限XX平台实名认证使用”。

核心是本地处理：图片不需要上传到服务器，处理后会输出一张新的带水印图片，原图不会被覆盖。默认样式是灰色半透明斜向平铺，也可以通过普通或高级自定义调整颜色、透明度、字号、角度和间距。

它不能保证绝对防盗用，但能帮你在提交材料前把用途标清楚，减少裸传敏感图片的风险。
```

Tags:

```text
#证件水印 #图片水印 #隐私保护 #效率工具 #AI工具 #本地处理
```

## Privacy Blurb

```text
水印处理在本机完成，不调用在线水印服务，不主动上传图片，不覆盖原图。输出文件会保存为新的带水印图片。
```
