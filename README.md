# MarkPigeon

<div align="center">
  <!-- Logo Placeholder -->
  <img src="assets/icon.png" alt="MarkPigeon Logo" width="120">
  
  <h3>Turn Markdown into Beautiful, Shareable HTML.</h3>

  [![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/steven-jianhao-li/MarkPigeon/releases)
  [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
  [![Downloads](https://img.shields.io/github/downloads/steven-jianhao-li/MarkPigeon/total)](https://github.com/steven-jianhao-li/MarkPigeon/releases)
  [![Build Status](https://img.shields.io/github/actions/workflow/status/steven-jianhao-li/MarkPigeon/ci.yml)](https://github.com/steven-jianhao-li/MarkPigeon/actions)
</div>

---

**MarkPigeon** is a lightweight tool designed for researchers and writers. It converts Markdown files into styled HTML documents with **intelligent asset management**, making your docs truly portable.

[中文文档](README_CN.md) | [Download Latest Release](https://github.com/steven-jianhao-li/MarkPigeon/releases)

## ✨ Key Features

* **🚀 Out-of-the-Box**: **No Python required!** Just download the executable, double-click, and start converting.
* **🎨 Typora Synergy**: Seamlessly reuse your favorite Typora CSS themes. If it looks good in Typora, it looks good in MarkPigeon.
* **📦 Smart Asset Isolation**: Automatically extracts local images into a dedicated `assets_<filename>` folder and rewrites paths. No more broken images when sharing!
* **🤐 One-Click Zipping**: Batch export to individual Zip files for easy email sharing.
* **🌍 Multi-language**: Supports English and Simplified Chinese.
* **🖥️ GUI & CLI**: Use the modern graphical interface or integrate it into your scripts.

## 📸 Screenshots

![Main Interface](assets/screenshot_gui.png)
*Clean and modern GUI built with PySide6*

## 🚀 Quick Start

### Option 1: GUI (Recommended)
1. Download the executable from [Releases](https://github.com/steven-jianhao-li/MarkPigeon/releases).
2. Drag and drop your `.md` files.
3. Select a theme and click **Convert**.

### Option 2: CLI
```bash
# Convert a single file
markpigeon report.md --theme github

# Convert and create ZIP
markpigeon report.md --theme github --zip

# Convert entire directory
markpigeon docs/ --output dist/ --recursive

# List available themes
markpigeon --list-themes
```

## 📋 Export Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Default** | HTML + `assets_` folder | Local viewing, editing |
| **Individual ZIP** | Each MD → separate ZIP | Email single docs |
| **Batch ZIP** | All outputs → one ZIP | Share entire project |

## 🎨 Themes

MarkPigeon comes with a GitHub-style theme and supports any Typora-compatible CSS:

1. Place your `.css` file in the `themes/` directory
2. Select it from the theme dropdown (GUI) or use `--theme name` (CLI)

## 🛠️ Development

```bash
# 1. Clone the repository
git clone https://github.com/steven-jianhao-li/MarkPigeon.git
cd MarkPigeon

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run GUI
python -m src.main

# 5. Run tests
pytest
```

### Project Structure

```
MarkPigeon/
├── src/
│   ├── core/           # Business logic (no UI dependencies)
│   │   ├── i18n.py     # Internationalization
│   │   ├── parser.py   # Markdown parsing
│   │   ├── renderer.py # HTML rendering
│   │   ├── packer.py   # ZIP packaging
│   │   └── converter.py # Workflow orchestration
│   ├── interfaces/
│   │   ├── cli/        # Command-line interface
│   │   └── gui/        # Graphical interface
│   └── main.py         # Entry point
├── locales/            # Translation files
├── themes/             # CSS themes
└── scripts/            # Release scripts
```

## 🔄 Release Process

Use the automated release script:

```bash
python scripts/release.py

# The script will:
# 1. Check Git status
# 2. Ask for version bump type (major/minor/patch)
# 3. Update version in code
# 4. Create Git commit and tag
# 5. Push to trigger GitHub Actions
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=steven-jianhao-li/MarkPigeon&type=Date)](https://star-history.com/#steven-jianhao-li/MarkPigeon&Date)

## 👥 Contributors

Thanks to all the people who contribute to this project!

<a href="https://github.com/steven-jianhao-li/MarkPigeon/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=steven-jianhao-li/MarkPigeon" />
</a>

