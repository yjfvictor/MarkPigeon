MD-Forge 项目开发全案

文档版本: 1.0.0
最后更新: 2025-12-17
项目代号: MD-Forge

目录 (Table of Contents)

第一部分：产品规格说明书 (PRD)

第二部分：一键自动化发布脚本设计

第三部分：README 模板 (多语言)

第四部分：开发者速查表

第一部分：产品规格说明书 (PRD)

1. 项目愿景

开发一款跨平台、支持批量处理的 Markdown 转 HTML 工具，核心解决“图片资源路径依赖”和“Typora 主题复用”痛点，提供 GUI (图形界面) 与 CLI (命令行) 双模式，并支持国际化。

2. 架构设计 (Core-Interface 分离)

项目采用分层架构，确保业务逻辑可复用且易于测试。

Core Layer (src/core/): 纯业务逻辑层。

职责: 文件 IO、Markdown AST 解析、资源哈希与搬运、HTML 渲染模板、Zip 打包、i18n 字符串管理。

约束: 禁止依赖 UI 库 (Qt/Tkinter)，禁止直接 print (使用 logging)，返回结构化结果。

Interface Layer (src/interfaces/):

cli/: 命令行适配器 (argparse)。

gui/: 图形界面适配器 (推荐 PySide6)。

Infrastructure:

locales/: 存放翻译文件 (en.json, zh_CN.json)。

themes/: 存放 CSS 主题文件。

3. 核心功能详解

3.1 国际化 (i18n)

实现: 加载 locales/*.json。

自动检测: 启动时检测系统 Locale。

动态切换: GUI 设置中支持热切换语言 (需重启生效或实时刷新)。

3.2 智能资源隔离 (Smart Asset Isolation)

这是本工具的核心差异化功能。

逻辑: 解析 Markdown AST 提取所有 <img src="...">。

处理:

在输出目录创建配套文件夹：assets_{Filename}/。

将图片复制进去（若文件名冲突，追加 Hash）。

重写 HTML 中的 src 为相对路径（./assets_{Filename}/image.png）。

容错: 图片不存在时，生成占位图并记录 Warning，不中断流程。

3.3 导出与打包模式

Mode A (默认): 输出 .html 文件 + assets_xxx 文件夹。

Mode B (独立 Zip): 每个 MD 生成一个 Filename.zip (内含 HTML + 资源文件夹)，方便单发给他人。

Mode C (汇总 Zip): 将当次任务所有结果打包为 Batch_Output_{Time}.zip。

3.4 主题引擎

兼容性: 完美支持 Typora CSS 选择器。

注入: 读取 CSS 文件内容，直接内联写入 HTML <head><style>...</style></head>，确保单文件独立性。

第二部分：一键自动化发布脚本设计

为了避免繁琐的 git tag 操作，我们将实现一个类似 npm release 的脚本。

脚本位置: scripts/release.py

功能逻辑：

环境检查: 检查当前 Git 工作区是否干净 (Clean)。

版本选择: 交互式询问用户升级类型 (Major / Minor / Patch)。

Current: 1.0.0 -> Patch: 1.0.1 / Minor: 1.1.0 / Major: 2.0.0

文件更新:

自动正则替换 src/core/__init__.py 中的 __version__ = "x.y.z"。

Git 自动化:

git add src/core/__init__.py

git commit -m "chore(release): vX.Y.Z"

git tag vX.Y.Z

git push origin main

git push origin vX.Y.Z (这一步将触发 GitHub Actions 自动构建发布版)

示例代码 (供 AI 实现参考):

# 伪代码逻辑
import subprocess
import re

def release():
    # 1. Check Git Status
    if "nothing to commit" not in subprocess.getoutput("git status"):
        print("❌ Error: Git working directory is not clean.")
        return

    # 2. Read current version from src/core/__init__.py
    # 3. Calculate new version based on user input
    # 4. Write new version back to file

    # 5. Execute Git Commands
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"chore(release): v{new_version}"])
    subprocess.run(["git", "tag", f"v{new_version}"])
    
    print(f"🚀 Ready to push v{new_version}. Continue? [y/N]")
    if input() == 'y':
        subprocess.run(["git", "push"])
        subprocess.run(["git", "push", "--tags"])
        print("✅ Done! GitHub Action triggered.")


第三部分：README 模板 (多语言)

请 AI 按照以下内容生成两个文件：README.md 和 README_CN.md。

1. 英文版 (README.md)

# MD-Forge

<div align="center">
  <!-- Logo Placeholder -->
  <img src="assets/icon.png" alt="MD-Forge Logo" width="120">
  
  <h3>Turn Markdown into Beautiful, Shareable HTML.</h3>

  [![Build Status](https://img.shields.io/github/actions/workflow/status/yourname/md-forge/ci.yml)](https://github.com/yourname/md-forge/actions)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://www.python.org/)
</div>

---

**MD-Forge** is a lightweight tool designed for researchers and writers. It converts Markdown files into styled HTML documents with **intelligent asset management**, making your docs truly portable.

[中文文档](README_CN.md) | [Download Latest Release](https://github.com/yourname/md-forge/releases)

## ✨ Key Features

* **🎨 Typora Theme Compatible**: Use any `.css` theme from Typora directly.
* **📦 Smart Asset Isolation**: Automatically extracts local images into a dedicated `assets_<filename>` folder and rewrites paths. No more broken images when sharing!
* **🤐 One-Click Zipping**: Batch export to individual Zip files for easy email sharing.
* **🌍 Multi-language**: Supports English and Simplified Chinese.
* **🖥️ GUI & CLI**: Use the modern graphical interface or integrate it into your scripts.

## 📸 Screenshots

![Main Interface](assets/screenshot_gui.png)
*Clean and modern GUI built with PySide6*

## 🚀 Quick Start

### Option 1: GUI (Recommended)
1. Download the executable from [Releases](https://github.com/yourname/md-forge/releases).
2. Drag and drop your `.md` files.
3. Select a theme and click **Convert**.

### Option 2: CLI
```bash
mdforge report.md --theme github --zip


🛠️ Development

# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run GUI
python src/main.py

# 3. Run Tests
pytest


📄 License

MIT License.


### 2. 中文版 (README_CN.md)

```markdown
# MD-Forge

<div align="center">
  <!-- Logo Placeholder -->
  <img src="assets/icon.png" alt="MD-Forge Logo" width="120">
  
  <h3>让 Markdown 文档分享变得优雅简单。</h3>
</div>

---

**MD-Forge** 是一款专为科研人员和作者设计的工具。它能将 Markdown 批量转换为带样式的 HTML，并**智能打包本地图片资源**，彻底解决“发给别人图片就挂了”的痛点。

[English Docs](README.md) | [下载最新版](https://github.com/yourname/md-forge/releases)

## ✨ 核心功能

* **🎨 复用 Typora 主题**: 直接把 `.css` 放入 `themes` 文件夹即可使用，完美还原样式。
* **📦 智能资源隔离**: 自动提取文档中的图片，复制到独立的 `assets_<文件名>` 文件夹，并自动修正 HTML 路径。
* **🤐 一键压缩打包**: 支持将每个文档及其资源单独打包成 Zip，方便微信/邮件发送。
* **🌍 多语言支持**: 界面支持 简体中文 / English。
* **🖥️ 双模式**: 提供易用的图形界面 (GUI) 和 高效的命令行 (CLI)。

## 📸 软件截图

![主界面](assets/screenshot_gui.png)

## 🚀 快速开始

### 方法 1: 使用界面版 (推荐)
1. 在 [Releases](https://github.com/yourname/md-forge/releases) 下载最新版。
2. 拖入 Markdown 文件或文件夹。
3. 选择喜欢的主题（如 GitHub, Night），点击 **开始转换**。

### 方法 2: 命令行
```bash
# 转换并打包为 Zip
mdforge report.md --theme newsprint --zip


🛠️ 开发者指南

如果您想参与开发：

环境配置:

pip install -r requirements.txt


运行测试:

pytest


发布新版本:

python scripts/release.py



---

## 第四部分：开发者速查表

> 这一部分供您个人参考，涵盖项目维护周期的核心命令。

### 1. 初始化开发环境
```bash
# 创建虚拟环境
python -m venv venv
# 激活环境 (Windows)
.\venv\Scripts\activate
# 安装所有依赖
pip install -r requirements.txt


2. 日常开发与测试

# 运行单元测试
pytest

# 检查代码风格 (使用 Ruff)
ruff check src/

# 自动修复部分错误
ruff check src/ --fix


# 启动 GUI 进行调试
python src/main.py


3. 一键发布新版本 (核心需求)

不需要手动打 Tag，直接运行我们设计的脚本：

# 运行发布向导
python scripts/release.py

# 向导会提示：
# ? Select release type:
# 1) Patch (1.0.0 -> 1.0.1)
# 2) Minor (1.0.0 -> 1.1.0)
# 3) Major (1.0.0 -> 2.0.0)
# 
# 确认后，脚本自动完成 Commit -> Tag -> Push


4. 手动打包测试 (不发版)

验证打包后的 exe 是否能正常运行：

pyinstaller build_scripts/mdforge.spec
# 产物在 dist/ 目录下
