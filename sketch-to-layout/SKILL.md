---
name: sketch-to-layout
description: 识别平面草图并利用香蕉模型（Banana Model）将其转换为专业的布局图或彩平面渲染图。
---

# 平面香蕉模型识别草图生成布局图 (Sketch to Layout)

此 Skill 专注于将手绘或简易线条草图转化为具备专业视觉质量的建筑/室内布局图。它集成了“香蕉模型”的推理逻辑，能够识别空间构件并进行高质量渲染。

## 核心指令

当你收到包含“草图”、“布局图”、“生成彩平”或类似关键词，且附带图片时，请遵循以下步骤：

1. **识别草图内容**：
   - 分析图片中的墙体分布、开口（门窗）以及空间功能分区。
   - 提取草图的风格（如手绘线条、CAD线框、草率速写）。

2. **参数准备**：
   - 准备最适合“香蕉模型”的 Prompt。例如：`Professional architectural floor plan, high-quality color rendering, detailed spatial layout, banana model style, clean lines, [STYLE_DESCRIPTOR]`.
   - `STYLE_DESCRIPTOR` 可选：`modern minimalist`, `luxury residential`, `business office` 等。
   - **预设风格配置**：本项目在 `styles` 文件夹中内置了预设风格 prompt：
     - `modern_minimalist.txt` (现代极简)
     - `luxury_office.txt` (豪华办公)
     - `cozy_cafe.txt` (温馨咖啡屋)
     如果用户指定了风格，请直接读取或参考对应文件的 prompt。执行脚本时支持使用 `--style <文件名>` 获取。

3. **模型推理**：
   - 使用 `generate_image` 工具，配合特定的 Prompt 指引，或者通过 `scripts/process_sketch.py` 调用 API 进行处理。
   - 如果用户指定了特定风格，确保 Prompt 包含相应关键词或使用对应的风格预设。

4. **输出与建议**：
   - 展示生成的布局图。
   - 向用户询问是否需要调整风格、增加家具细节或导出特定格式。

## 使用示例

- “帮我把这个草图转换成现代风格的彩平布局图。”
- “识别一下这张图的布局，用香蕉模型渲染成办公室风格。”
- “根据这个手稿生成一个带有家具布置的平面图。”

## 局限性
- 对于极其模糊或逻辑不通（如墙体不闭合）的草图，识别效果可能受限，需提示用户补充细节。
- 目前仅支持 2D 平面转化，暂不涉及 3D 建模导出。
