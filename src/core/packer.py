"""
MarkPigeon Zip Packer Module

Provides ZIP packaging functionality for HTML outputs.
"""

import logging
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PackResult:
    """Result of a packing operation."""

    zip_file: Path | None = None  # Path to created ZIP file
    files_packed: list[str] = field(default_factory=list)  # List of files in ZIP
    success: bool = True
    error: str | None = None


class ExportMode:
    """Export mode constants."""

    DEFAULT = "default"  # Mode A: .html + assets_xxx folder
    INDIVIDUAL_ZIP = "zip"  # Mode B: Each MD -> individual .zip
    BATCH_ZIP = "batch"  # Mode C: All results -> single .zip


class ZipPacker:
    """
    Handles ZIP packaging for MarkPigeon outputs.

    Supports three modes:
    - DEFAULT: No zipping, just HTML + assets folder
    - INDIVIDUAL_ZIP: Each document becomes its own ZIP
    - BATCH_ZIP: All documents packed into a single ZIP
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the packer.

        Args:
            output_dir: Base output directory
        """
        self.output_dir = Path(output_dir)

    def pack_individual(self, html_file: Path, assets_dir: Path | None = None) -> PackResult:
        """
        Pack a single HTML file and its assets into a ZIP.

        Args:
            html_file: Path to the HTML file
            assets_dir: Optional path to the assets directory

        Returns:
            PackResult with ZIP information.
        """
        result = PackResult()

        if not html_file.exists():
            result.success = False
            result.error = f"HTML file not found: {html_file}"
            return result

        # Create ZIP filename
        zip_name = f"{html_file.stem}.zip"
        zip_path = html_file.parent / zip_name

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add HTML file
                zf.write(html_file, html_file.name)
                result.files_packed.append(html_file.name)

                # Add assets directory if exists
                if assets_dir and assets_dir.exists():
                    for asset_file in assets_dir.rglob("*"):
                        if asset_file.is_file():
                            arcname = f"{assets_dir.name}/{asset_file.relative_to(assets_dir)}"
                            zf.write(asset_file, arcname)
                            result.files_packed.append(arcname)

            result.zip_file = zip_path
            logger.info(f"Created ZIP: {zip_path} ({len(result.files_packed)} files)")

        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"Failed to create ZIP: {e}")

        return result

    def pack_batch(
        self,
        items: list[tuple],  # List of (html_file, assets_dir) tuples
        zip_name: str | None = None,
    ) -> PackResult:
        """
        Pack multiple HTML files and their assets into a single ZIP.

        Args:
            items: List of (html_file, assets_dir) tuples
            zip_name: Optional custom ZIP filename

        Returns:
            PackResult with ZIP information.
        """
        result = PackResult()

        if not items:
            result.success = False
            result.error = "No items to pack"
            return result

        # Generate ZIP filename
        if zip_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"Batch_Output_{timestamp}.zip"

        zip_path = self.output_dir / zip_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for html_file, assets_dir in items:
                    html_file = Path(html_file)

                    if not html_file.exists():
                        logger.warning(f"Skipping missing file: {html_file}")
                        continue

                    # Add HTML file
                    zf.write(html_file, html_file.name)
                    result.files_packed.append(html_file.name)

                    # Add assets directory if exists
                    if assets_dir:
                        assets_dir = Path(assets_dir)
                        if assets_dir.exists():
                            for asset_file in assets_dir.rglob("*"):
                                if asset_file.is_file():
                                    arcname = (
                                        f"{assets_dir.name}/{asset_file.relative_to(assets_dir)}"
                                    )
                                    zf.write(asset_file, arcname)
                                    result.files_packed.append(arcname)

            result.zip_file = zip_path
            logger.info(f"Created batch ZIP: {zip_path} ({len(result.files_packed)} files)")

        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"Failed to create batch ZIP: {e}")

        return result

    def cleanup_after_zip(self, html_file: Path, assets_dir: Path | None = None) -> bool:
        """
        Clean up original files after successful ZIP creation.

        Args:
            html_file: HTML file to remove
            assets_dir: Assets directory to remove

        Returns:
            True if cleanup successful.
        """
        try:
            if html_file.exists():
                html_file.unlink()

            if assets_dir and assets_dir.exists():
                import shutil

                shutil.rmtree(assets_dir)

            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False


def pack_to_zip(html_file: Path, assets_dir: Path | None = None) -> PackResult:
    """
    Convenience function to pack a single file to ZIP.

    Args:
        html_file: Path to HTML file
        assets_dir: Optional assets directory

    Returns:
        PackResult object.
    """
    packer = ZipPacker(html_file.parent)
    return packer.pack_individual(html_file, assets_dir)
