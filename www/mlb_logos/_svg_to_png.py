#!/usr/bin/env python3
"""
Convert SVG files to 70x70 PNG images.
Usage: python svg_to_png.py [input_directory] [output_directory]
"""

import sys
from pathlib import Path
import cairosvg


def convert_svg_to_png(svg_path: Path, output_path: Path, size: int = 70) -> None:
    """Convert a single SVG file to PNG at specified size."""
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(output_path),
            output_width=size,
            output_height=size
        )
        print(f"✓ Converted: {svg_path.name} -> {output_path.name}")
    except Exception as e:
        print(f"✗ Failed to convert {svg_path.name}: {e}")


def main():
    # Parse arguments
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = Path.cwd()
    
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = input_dir / "png_output"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all SVG files
    svg_files = list(input_dir.glob("*.svg"))
    
    if not svg_files:
        print(f"No SVG files found in {input_dir}")
        return
    
    print(f"Found {len(svg_files)} SVG files")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Convert each SVG
    for svg_file in sorted(svg_files):
        output_file = output_dir / f"{svg_file.stem}.png"
        convert_svg_to_png(svg_file, output_file)
    
    print("-" * 50)
    print(f"Conversion complete! Check {output_dir}")


if __name__ == "__main__":
    main()
