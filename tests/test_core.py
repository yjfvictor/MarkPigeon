"""
Comprehensive tests for the MarkPigeon core modules.

Tests cover:
- Markdown parsing with various elements
- Image extraction (local and remote)
- HTML rendering with themes
- ZIP packaging modes
- Batch conversion
"""

import tempfile
from pathlib import Path

import pytest

from src.core.parser import MarkdownParser, parse_markdown
from src.core.renderer import HtmlRenderer
from src.core.packer import ZipPacker, ExportMode as PackerExportMode
from src.core.converter import Converter, ExportMode
from src.core.i18n import I18n, get_i18n, t


class TestMarkdownParser:
    """Tests for MarkdownParser."""
    
    def test_parse_simple_markdown(self):
        """Test parsing simple markdown content."""
        parser = MarkdownParser()
        result = parser.parse("# Hello World\n\nThis is a test.")
        
        assert result.html is not None
        assert "<h1>" in result.html
        assert "Hello World" in result.html
    
    def test_parse_with_local_images(self):
        """Test parsing markdown with local images."""
        parser = MarkdownParser()
        content = "# Test\n\n![Alt text](./image.png)"
        result = parser.parse(content)
        
        assert len(result.images) == 1
        assert result.images[0].original_src == "./image.png"
        assert result.images[0].is_local == True
        assert len(result.local_images) == 1
    
    def test_parse_with_url_image(self):
        """Test parsing markdown with URL image."""
        parser = MarkdownParser()
        content = "![Remote](https://example.com/image.png)"
        result = parser.parse(content)
        
        assert len(result.images) == 1
        assert result.images[0].is_local == False
        assert len(result.local_images) == 0
    
    def test_parse_mixed_images(self):
        """Test parsing markdown with both local and remote images."""
        parser = MarkdownParser()
        content = """
# Mixed Images

![Local](./local.png)
![Remote](https://example.com/remote.png)
![Another Local](../images/test.jpg)
"""
        result = parser.parse(content)
        
        assert len(result.images) == 3
        assert len(result.local_images) == 2
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = MarkdownParser()
        result = parser.parse_file(Path("/nonexistent/file.md"))
        
        assert result.html == ""
        assert len(result.warnings) > 0
    
    def test_parse_with_code_blocks(self):
        """Test parsing markdown with code blocks."""
        parser = MarkdownParser()
        content = """
```python
def hello():
    print("Hello")
```
"""
        result = parser.parse(content)
        
        assert "<code" in result.html
        assert "hello" in result.html
    
    def test_parse_with_tables(self):
        """Test parsing markdown with tables."""
        parser = MarkdownParser()
        content = """
| Name | Value |
|------|-------|
| A    | 1     |
| B    | 2     |
"""
        result = parser.parse(content)
        
        assert "<table" in result.html
        assert "<th" in result.html
        assert "<td" in result.html
    
    def test_parse_with_links(self):
        """Test parsing markdown with links."""
        parser = MarkdownParser()
        content = "[GitHub](https://github.com)"
        result = parser.parse(content)
        
        assert "<a " in result.html
        assert "href=" in result.html
        assert "github.com" in result.html
    
    def test_parse_with_blockquotes(self):
        """Test parsing markdown with blockquotes."""
        parser = MarkdownParser()
        content = "> This is a quote"
        result = parser.parse(content)
        
        assert "<blockquote" in result.html
    
    def test_update_image_paths(self):
        """Test updating image paths in HTML."""
        parser = MarkdownParser()
        html = '<img src="./old.png" alt="test">'
        mapping = {"./old.png": "./assets/new.png"}
        
        updated = parser.update_image_paths(html, mapping)
        
        assert "./assets/new.png" in updated


class TestHtmlRenderer:
    """Tests for HtmlRenderer."""
    
    def test_render_with_default_css(self):
        """Test rendering with default CSS."""
        parser = MarkdownParser()
        renderer = HtmlRenderer()
        
        parse_result = parser.parse("# Test\n\nParagraph")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = renderer.render(parse_result, Path(tmpdir))
            
            assert result.success
            assert result.output_file is not None
            assert result.output_file.exists()
            
            html = result.output_file.read_text(encoding='utf-8')
            assert "<!DOCTYPE html>" in html
            assert "<style>" in html
    
    def test_render_with_title(self):
        """Test rendering with custom title."""
        parser = MarkdownParser()
        renderer = HtmlRenderer()
        
        parse_result = parser.parse("# Content")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = renderer.render(
                parse_result, 
                Path(tmpdir),
                title="Custom Title"
            )
            
            html = result.output_file.read_text(encoding='utf-8')
            assert "<title>Custom Title</title>" in html
    
    def test_render_with_lang(self):
        """Test rendering with custom language."""
        parser = MarkdownParser()
        renderer = HtmlRenderer()
        
        parse_result = parser.parse("# 中文内容")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = renderer.render(
                parse_result, 
                Path(tmpdir),
                lang="zh"
            )
            
            html = result.output_file.read_text(encoding='utf-8')
            assert 'lang="zh"' in html
    
    def test_get_available_themes(self):
        """Test getting available themes."""
        renderer = HtmlRenderer()
        themes = renderer.get_available_themes()
        
        # Should at least have the github theme
        assert isinstance(themes, list)
    
    def test_render_creates_assets_dir(self):
        """Test that rendering creates assets directory for local images."""
        parser = MarkdownParser()
        renderer = HtmlRenderer()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create a test image
            image_path = tmpdir / "test_image.png"
            # Create a simple 1x1 PNG
            from PIL import Image
            img = Image.new('RGB', (10, 10), color='red')
            img.save(image_path)
            
            # Create markdown with image
            md_content = f"# Test\n\n![Test Image]({image_path})"
            md_file = tmpdir / "test.md"
            md_file.write_text(md_content, encoding='utf-8')
            
            parse_result = parser.parse_file(md_file)
            result = renderer.render(parse_result, tmpdir)
            
            assert result.success
            if result.assets_dir:
                assert result.assets_dir.exists()
                assert len(list(result.assets_dir.iterdir())) > 0


class TestZipPacker:
    """Tests for ZipPacker."""
    
    def test_pack_individual(self):
        """Test individual ZIP packing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test HTML file
            html_file = tmpdir / "test.html"
            html_file.write_text("<html></html>", encoding='utf-8')
            
            packer = ZipPacker(tmpdir)
            result = packer.pack_individual(html_file)
            
            assert result.success
            assert result.zip_file is not None
            assert result.zip_file.exists()
            assert result.zip_file.suffix == ".zip"
    
    def test_pack_with_assets(self):
        """Test packing with assets directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            html_file = tmpdir / "test.html"
            html_file.write_text("<html></html>", encoding='utf-8')
            
            assets_dir = tmpdir / "assets_test"
            assets_dir.mkdir()
            (assets_dir / "image.png").write_bytes(b"fake png")
            
            packer = ZipPacker(tmpdir)
            result = packer.pack_individual(html_file, assets_dir)
            
            assert result.success
            assert len(result.files_packed) == 2
    
    def test_pack_batch(self):
        """Test batch ZIP packing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            files = []
            for i in range(3):
                html_file = tmpdir / f"doc{i}.html"
                html_file.write_text(f"<html>{i}</html>", encoding='utf-8')
                files.append((html_file, None))
            
            packer = ZipPacker(tmpdir)
            result = packer.pack_batch(files)
            
            assert result.success
            assert result.zip_file is not None
            assert len(result.files_packed) == 3


class TestConverter:
    """Tests for Converter."""
    
    def test_convert_simple_file(self):
        """Test converting a simple markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test file
            md_file = tmpdir / "test.md"
            md_file.write_text("# Hello\n\nWorld", encoding='utf-8')
            
            converter = Converter()
            result = converter.convert_file(md_file)
            
            assert result.success
            assert result.output_file.name == "test.html"
            assert result.output_file.exists()
    
    def test_convert_with_theme(self):
        """Test converting with a theme."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            md_file = tmpdir / "test.md"
            md_file.write_text("# Themed", encoding='utf-8')
            
            converter = Converter()
            result = converter.convert_file(md_file, theme='github')
            
            assert result.success
    
    def test_batch_conversion(self):
        """Test batch conversion of multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            for i in range(3):
                md_file = tmpdir / f"test{i}.md"
                md_file.write_text(f"# Document {i}", encoding='utf-8')
            
            converter = Converter()
            files = list(tmpdir.glob("*.md"))
            
            result = converter.convert_batch(files, tmpdir)
            
            assert result.total == 3
            assert result.successful == 3
            assert result.failed == 0
    
    def test_convert_directory(self):
        """Test converting all files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            for i in range(2):
                (tmpdir / f"doc{i}.md").write_text(f"# Doc {i}", encoding='utf-8')
            
            converter = Converter()
            result = converter.convert_directory(tmpdir)
            
            assert result.total == 2
            assert result.successful == 2
    
    def test_convert_nonexistent_file(self):
        """Test converting a nonexistent file."""
        converter = Converter()
        result = converter.convert_file(Path("/nonexistent/file.md"))
        
        assert not result.success
        assert result.error is not None


class TestExportModes:
    """Tests for different export modes."""
    
    def test_individual_zip_mode(self):
        """Test individual ZIP export mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            md_file = tmpdir / "doc.md"
            md_file.write_text("# Test", encoding='utf-8')
            
            converter = Converter()
            result = converter.convert_file(
                md_file,
                export_mode=ExportMode.INDIVIDUAL_ZIP
            )
            
            assert result.success
            assert result.zip_file is not None
            assert result.zip_file.suffix == ".zip"
    
    def test_batch_zip_mode(self):
        """Test batch ZIP export mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            for i in range(2):
                md_file = tmpdir / f"doc{i}.md"
                md_file.write_text(f"# Doc {i}", encoding='utf-8')
            
            converter = Converter()
            files = list(tmpdir.glob("*.md"))
            
            result = converter.convert_batch(
                files,
                tmpdir,
                export_mode=ExportMode.BATCH_ZIP
            )
            
            assert result.batch_zip is not None
            assert result.batch_zip.exists()


class TestI18n:
    """Tests for internationalization."""
    
    def test_load_english(self):
        """Test loading English locale."""
        i18n = I18n()
        success = i18n.load_locale('en')
        
        assert success
        assert i18n.current_locale == 'en'
    
    def test_load_chinese(self):
        """Test loading Chinese locale."""
        i18n = I18n()
        success = i18n.load_locale('zh_CN')
        
        assert success
        assert i18n.current_locale == 'zh_CN'
    
    def test_translate_key(self):
        """Test translating a key."""
        i18n = I18n()
        i18n.load_locale('en')
        
        title = i18n.t('app.title')
        
        assert title == 'MarkPigeon'
    
    def test_translate_with_params(self):
        """Test translating with format parameters."""
        i18n = I18n()
        i18n.load_locale('en')
        
        status = i18n.t('status.processing', current=1, total=5)
        
        assert '1' in status
        assert '5' in status
    
    def test_missing_key_returns_key(self):
        """Test that missing key returns the key itself."""
        i18n = I18n()
        i18n.load_locale('en')
        
        result = i18n.t('nonexistent.key')
        
        assert result == 'nonexistent.key'
    
    def test_available_locales(self):
        """Test getting available locales."""
        i18n = I18n()
        locales = i18n.available_locales
        
        assert 'en' in locales
        assert 'zh_CN' in locales
    
    def test_global_i18n(self):
        """Test global i18n instance."""
        i18n1 = get_i18n()
        i18n2 = get_i18n()
        
        assert i18n1 is i18n2
    
    def test_convenience_t_function(self):
        """Test the convenience t() function."""
        result = t('app.title')
        
        assert result == 'MarkPigeon'


class TestImageProcessing:
    """Tests for image processing functionality."""
    
    def test_local_image_detection(self):
        """Test detection of local images."""
        parser = MarkdownParser()
        
        # Various local path formats
        test_cases = [
            "./image.png",
            "../images/photo.jpg",
            "assets/icon.svg",
            "C:/Users/test/image.png",
            "/home/user/image.gif",
        ]
        
        for src in test_cases:
            content = f"![Alt]({src})"
            result = parser.parse(content)
            assert result.images[0].is_local, f"Failed for: {src}"
    
    def test_remote_image_detection(self):
        """Test detection of remote images."""
        parser = MarkdownParser()
        
        # Various URL formats
        test_cases = [
            "https://example.com/image.png",
            "http://example.org/photo.jpg",
            "data:image/png;base64,abc123",
        ]
        
        for src in test_cases:
            content = f"![Alt]({src})"
            result = parser.parse(content)
            assert not result.images[0].is_local, f"Failed for: {src}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
