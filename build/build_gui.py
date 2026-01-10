#!/usr/bin/env python3
"""Build script for packaging GUI as standalone executable"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Build the GUI executable"""
    # Get paths
    build_dir = Path(__file__).parent
    project_root = build_dir.parent
    spec_file = build_dir / "gui.spec"
    
    print("=" * 70)
    print("Trash Collection Route Generator - GUI Packaging")
    print("=" * 70)
    print()
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    print()
    print("Building executable...")
    print(f"Spec file: {spec_file}")
    print()
    
    # Change to project root
    os.chdir(project_root)
    
    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        str(spec_file)
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 70)
        print("✓ Build complete!")
        print(f"Executable location: {project_root / 'dist' / 'TrashRouteGenerator.exe'}")
        print("=" * 70)
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 70)
        print(f"✗ Build failed: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
