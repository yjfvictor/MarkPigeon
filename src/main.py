"""
MarkPigeon Main Entry Point

Determines whether to launch GUI or CLI based on arguments.
"""

import sys


def main():
    """
    Main entry point for MarkPigeon.

    - No arguments: Launch GUI
    - With arguments: Run CLI
    """
    if len(sys.argv) > 1:
        # CLI mode
        from .interfaces.cli.main import main as cli_main

        sys.exit(cli_main())
    else:
        # GUI mode
        try:
            from .interfaces.gui.main_window import run_gui

            run_gui()
        except ImportError as e:
            print(f"Error: GUI dependencies not available: {e}")
            print("Please install PySide6: pip install PySide6")
            print("\nAlternatively, use CLI mode:")
            print("  markpigeon document.md --help")
            sys.exit(1)


if __name__ == "__main__":
    main()
