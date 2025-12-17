"""
MarkPigeon Markdown Parser Module

Parses Markdown files and extracts embedded resources (images).
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

logger = logging.getLogger(__name__)


@dataclass
class ImageInfo:
    """Information about an image found in the markdown."""
    original_src: str      # Original src attribute value
    local_path: Optional[Path]  # Resolved local file path (None if URL or not found)
    is_local: bool         # True if it's a local file reference
    exists: bool           # True if the local file exists
    alt_text: str = ""     # Alt text from the image tag


@dataclass
class ParseResult:
    """Result of parsing a Markdown file."""
    html: str                          # Generated HTML content
    images: List[ImageInfo] = field(default_factory=list)  # All images found
    local_images: List[ImageInfo] = field(default_factory=list)  # Local images only
    warnings: List[str] = field(default_factory=list)  # Warning messages
    source_file: Optional[Path] = None  # Original markdown file path


class MarkdownParser:
    """
    Parses Markdown content and extracts image resources.
    
    Uses markdown-it-py for Markdown parsing and BeautifulSoup
    for HTML analysis and modification.
    """
    
    def __init__(self):
        """Initialize the Markdown parser with standard plugins."""
        self.md = MarkdownIt('commonmark', {'html': True})
        # Enable common extensions
        self.md.enable('table')
        self.md.enable('strikethrough')
    
    def parse(self, content: str, source_file: Optional[Path] = None) -> ParseResult:
        """
        Parse Markdown content and extract image information.
        
        Args:
            content: Markdown content string
            source_file: Optional path to the source file (for resolving relative paths)
            
        Returns:
            ParseResult containing HTML and image information.
        """
        result = ParseResult(html="", source_file=source_file)
        
        # Convert Markdown to HTML
        try:
            result.html = self.md.render(content)
        except Exception as e:
            logger.error(f"Failed to parse Markdown: {e}")
            result.warnings.append(f"Markdown parsing error: {e}")
            return result
        
        # Extract images from HTML
        result.images = self._extract_images(result.html, source_file)
        
        # Filter local images
        result.local_images = [img for img in result.images if img.is_local]
        
        # Add warnings for missing images
        for img in result.local_images:
            if not img.exists:
                warning = f"Image not found: {img.original_src}"
                result.warnings.append(warning)
                logger.warning(warning)
        
        return result
    
    def parse_file(self, file_path: Path) -> ParseResult:
        """
        Parse a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            ParseResult containing HTML and image information.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return ParseResult(
                html="",
                warnings=[f"File not found: {file_path}"],
                source_file=file_path
            )
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ParseResult(
                html="",
                warnings=[f"Failed to read file: {e}"],
                source_file=file_path
            )
        
        return self.parse(content, source_file=file_path)
    
    def _extract_images(
        self, 
        html: str, 
        source_file: Optional[Path]
    ) -> List[ImageInfo]:
        """
        Extract all images from HTML content.
        
        Args:
            html: HTML content
            source_file: Source file path for resolving relative paths
            
        Returns:
            List of ImageInfo objects.
        """
        images = []
        soup = BeautifulSoup(html, 'lxml')
        
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src', '')
            alt = img_tag.get('alt', '')
            
            if not src:
                continue
            
            image_info = self._analyze_image_src(src, alt, source_file)
            images.append(image_info)
        
        return images
    
    def _analyze_image_src(
        self, 
        src: str, 
        alt: str,
        source_file: Optional[Path]
    ) -> ImageInfo:
        """
        Analyze an image src attribute to determine if it's local or remote.
        
        Args:
            src: The src attribute value
            alt: The alt text
            source_file: Source file for resolving relative paths
            
        Returns:
            ImageInfo object with analysis results.
        """
        # Decode URL-encoded characters
        decoded_src = unquote(src)
        
        # Check if it's a URL
        parsed = urlparse(decoded_src)
        if parsed.scheme in ('http', 'https', 'data'):
            return ImageInfo(
                original_src=src,
                local_path=None,
                is_local=False,
                exists=False,  # We don't check remote URLs
                alt_text=alt
            )
        
        # It's a local path
        # Remove file:// prefix if present
        local_src = decoded_src
        if local_src.startswith('file://'):
            local_src = local_src[7:]
            # Handle Windows paths like file:///C:/...
            if len(local_src) > 2 and local_src[0] == '/' and local_src[2] == ':':
                local_src = local_src[1:]
        
        # Resolve the path
        local_path = Path(local_src)
        
        if not local_path.is_absolute() and source_file:
            # Resolve relative to source file's directory
            local_path = (source_file.parent / local_path).resolve()
        
        exists = local_path.exists() and local_path.is_file()
        
        return ImageInfo(
            original_src=src,
            local_path=local_path if exists or local_path.is_absolute() else None,
            is_local=True,
            exists=exists,
            alt_text=alt
        )
    
    def update_image_paths(
        self, 
        html: str, 
        path_mapping: dict
    ) -> str:
        """
        Update image paths in HTML according to a mapping.
        
        Args:
            html: Original HTML content
            path_mapping: Dict mapping original src to new src
            
        Returns:
            Updated HTML with new image paths.
        """
        soup = BeautifulSoup(html, 'lxml')
        
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src', '')
            if src in path_mapping:
                img_tag['src'] = path_mapping[src]
        
        # Return just the body content without <html><body> wrapper
        body = soup.find('body')
        if body:
            return ''.join(str(child) for child in body.children)
        return str(soup)


def parse_markdown(content: str, source_file: Optional[Path] = None) -> ParseResult:
    """
    Convenience function to parse Markdown content.
    
    Args:
        content: Markdown content string
        source_file: Optional source file path
        
    Returns:
        ParseResult object.
    """
    parser = MarkdownParser()
    return parser.parse(content, source_file)


def parse_markdown_file(file_path: Path) -> ParseResult:
    """
    Convenience function to parse a Markdown file.
    
    Args:
        file_path: Path to the Markdown file
        
    Returns:
        ParseResult object.
    """
    parser = MarkdownParser()
    return parser.parse_file(file_path)
