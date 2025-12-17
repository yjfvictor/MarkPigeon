#!/usr/bin/env python3
"""
MarkPigeon Release Script

Automates the release process:
1. Check Git status
2. Bump version
3. Create commit and tag
4. Push to remote
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


# Version file path
VERSION_FILE = Path(__file__).parent.parent / 'src' / 'core' / '__init__.py'
VERSION_PATTERN = re.compile(r'__version__\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']')


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_current_version() -> Tuple[int, int, int]:
    """Get current version from __init__.py."""
    content = VERSION_FILE.read_text(encoding='utf-8')
    match = VERSION_PATTERN.search(content)
    
    if not match:
        raise ValueError(f"Could not find version in {VERSION_FILE}")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(major: int, minor: int, patch: int, bump_type: str) -> Tuple[int, int, int]:
    """Calculate new version based on bump type."""
    if bump_type == 'major':
        return major + 1, 0, 0
    elif bump_type == 'minor':
        return major, minor + 1, 0
    elif bump_type == 'patch':
        return major, minor, patch + 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_file(new_version: str) -> None:
    """Update version in __init__.py."""
    content = VERSION_FILE.read_text(encoding='utf-8')
    new_content = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    VERSION_FILE.write_text(new_content, encoding='utf-8')
    print(f"  Updated {VERSION_FILE}")


def check_git_clean() -> bool:
    """Check if Git working directory is clean."""
    result = run_command(['git', 'status', '--porcelain'], check=False)
    return result.stdout.strip() == ''


def git_add_commit_tag(version: str) -> None:
    """Create Git commit and tag."""
    run_command(['git', 'add', str(VERSION_FILE)])
    run_command(['git', 'commit', '-m', f'chore(release): v{version}'])
    run_command(['git', 'tag', f'v{version}'])


def git_push() -> None:
    """Push commits and tags to remote."""
    run_command(['git', 'push'])
    run_command(['git', 'push', '--tags'])


def get_user_choice() -> Optional[str]:
    """Get user's choice for version bump type."""
    print()
    print("Select release type:")
    print("  1) Patch (x.y.Z) - Bug fixes")
    print("  2) Minor (x.Y.0) - New features")
    print("  3) Major (X.0.0) - Breaking changes")
    print("  q) Quit")
    print()
    
    choice = input("Enter choice [1/2/3/q]: ").strip().lower()
    
    if choice == '1':
        return 'patch'
    elif choice == '2':
        return 'minor'
    elif choice == '3':
        return 'major'
    elif choice == 'q':
        return None
    else:
        print("Invalid choice!")
        return get_user_choice()


def confirm(message: str) -> bool:
    """Ask for confirmation."""
    response = input(f"{message} [y/N]: ").strip().lower()
    return response == 'y'


def main() -> int:
    """Main release workflow."""
    print()
    print("=" * 50)
    print("  🚀 MarkPigeon Release Script")
    print("=" * 50)
    print()
    
    # Step 1: Check Git status
    print("Checking Git status...")
    if not check_git_clean():
        print()
        print("❌ Error: Git working directory is not clean!")
        print("   Please commit or stash your changes first.")
        return 1
    print("  ✓ Working directory is clean")
    print()
    
    # Step 2: Get current version
    try:
        major, minor, patch = get_current_version()
        current = f"{major}.{minor}.{patch}"
        print(f"Current version: v{current}")
    except Exception as e:
        print(f"❌ Error reading version: {e}")
        return 1
    
    # Step 3: Get bump type
    bump_type = get_user_choice()
    if bump_type is None:
        print("Release cancelled.")
        return 0
    
    # Step 4: Calculate new version
    new_major, new_minor, new_patch = bump_version(major, minor, patch, bump_type)
    new_version = f"{new_major}.{new_minor}.{new_patch}"
    
    print()
    print(f"Version bump: v{current} → v{new_version}")
    print()
    
    # Step 5: Confirm
    if not confirm("Proceed with release?"):
        print("Release cancelled.")
        return 0
    
    print()
    print("Creating release...")
    print()
    
    # Step 6: Update version file
    print("[1/4] Updating version file...")
    try:
        update_version_file(new_version)
    except Exception as e:
        print(f"❌ Error updating version: {e}")
        return 1
    
    # Step 7: Git commit and tag
    print("[2/4] Creating Git commit and tag...")
    try:
        git_add_commit_tag(new_version)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e.stderr}")
        return 1
    
    # Step 8: Confirm push
    print()
    print(f"Ready to push v{new_version} to remote.")
    if not confirm("Push to origin?"):
        print()
        print("⚠️  Local release created but not pushed.")
        print("   Run these commands manually when ready:")
        print("     git push")
        print("     git push --tags")
        return 0
    
    # Step 9: Push
    print("[3/4] Pushing to remote...")
    try:
        git_push()
    except subprocess.CalledProcessError as e:
        print(f"❌ Push error: {e.stderr}")
        return 1
    
    # Done!
    print("[4/4] Done!")
    print()
    print("=" * 50)
    print(f"  ✅ Released v{new_version} successfully!")
    print("=" * 50)
    print()
    print("GitHub Actions will now build and publish the release.")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
