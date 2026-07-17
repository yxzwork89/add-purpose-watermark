# 用途水印 / Purpose Watermark

一个用于 Codex 的本地图片水印 Skill。给身份证、证件照、营业执照、合同、户口本、证书等图片添加“仅供某用途使用”的平铺文字水印。

图片在本机处理，不调用在线水印 API，不主动上传图片，也不覆盖原图。

> A local-first Codex Skill for adding tiled purpose watermarks to document images before sharing or submission.

## 功能

- 支持 JPG/JPEG、PNG、WebP、BMP 和 TIFF
- 支持单图、多图和目录批量处理
- 默认灰色、半透明、左下至右上的交错平铺水印
- 保持原图尺寸、原格式以及可读取的编码质量参数
- 输出文件默认追加 `_watermark`
- 支持中文、英文和多行水印文案
- 全程本地处理，不覆盖原图

## 交互模式

| 模式 | 触发方式 | 行为 |
| --- | --- | --- |
| 默认 | 直接提供图片和文案 | 使用默认样式立即处理 |
| 普通自定义 | “自定义水印”“水印+自定义” | 补齐文案、颜色、透明度、字号 |
| 高级自定义 | “高级自定义”“高级设置” | 在普通自定义基础上补齐角度和横纵间距 |

Prompt 已明确的属性会自动跳过，不重复询问。所有配置完成后，Skill 会展示一次完整汇总，得到最终确认后再生成图片。

## 示例 Prompt

```text
给这张身份证图片添加水印：仅限 XX 平台实名认证使用
```

```text
给这批合同照片自定义添加水印，文案：仅供合同审核使用，颜色红色
```

```text
高级自定义水印：文案“仅供租房备案使用”，透明度 30%，角度 0 度
```

## 安装

让 Codex 从本仓库安装 `add-purpose-watermark/` 目录，或手动执行：

```bash
git clone https://github.com/yxzwork89/add-purpose-watermark.git
cp -R add-purpose-watermark/add-purpose-watermark ~/.codex/skills/
```

安装后，在新的 Codex 任务中使用 `$add-purpose-watermark`。

## 依赖

渲染脚本使用 Python 和 Pillow：

```bash
python3 -m pip install pillow
```

安装依赖前应先获得用户许可。Skill 不需要在线图片处理服务。

## CLI

```bash
python3 add-purpose-watermark/scripts/apply_watermark.py \
  --input "/path/to/front.jpg" \
  --input "/path/to/back.jpg" \
  --text "仅限 XX 平台实名认证使用"
```

常用可选参数：

```text
--color #6B7280
--opacity 60
--size small|medium|large|xlarge
--angle -30
--gap-x 40
--gap-y 40
--output-dir /path/to/output
```

默认输出名称：

```text
原文件名_watermark.原扩展名
```

## 隐私与边界

- 图片只在本机指定路径中读写
- 不调用在线水印 API，不主动上传图片
- 不删除或覆盖原图
- 水印用于明确材料用途和降低裸传风险，不承诺绝对防盗用或法律保护效果
- Skill 不包含浏览器上传控件注入、云同步或长期图片存储

## Repository Layout

```text
add-purpose-watermark/
├── README.md
├── LICENSE
├── docs/
│   └── SHARE_COPY.md
└── add-purpose-watermark/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── scripts/
    └── references/
```

## License

[MIT](LICENSE)
