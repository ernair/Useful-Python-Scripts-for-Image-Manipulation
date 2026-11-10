"""
Single ICO Packer (Transparent PNG to Windows .ico Container via Click)
======================================================================
Converts an already transparent PNG image into a properly packed Windows 
.ico container with all standard resolution layers.

It utilizes the 'click' library for clean argument parsing, automated validation, 
and native terminal coloring.

Prerequisites:
    pip install Pillow click

Usage:
    python png_to_ico.py <path_to_transparent_png>
"""

import os
import sys
import click
from PIL import Image

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('png_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def pack_ico(png_path):
    """Single ICO Packer.
    
    Converts an already transparent PNG image into a properly packed Windows 
    .ico container with 6 standard resolution scaling layers (16x16 to 256x256).
    """
    if not png_path.lower().endswith('.png'):
        click.secho("Error: Input file must be a PNG image.", fg='red', bold=True)
        return

    file_name_without_ext, _ = os.path.splitext(png_path)
    ico_path = f"{file_name_without_ext}.ico"

    try:
        click.echo(f"Packing '{png_path}' into an ICO container...")
        with Image.open(png_path) as img:
            # Define standard Windows desktop icon sizes
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Save directly as ICO with embedded sizes
            img.save(ico_path, format="ICO", sizes=icon_sizes)
            click.secho(f"Success! Windows Icon saved as: {ico_path}", fg='green', bold=True)

    except Exception as e:
        click.secho(f"Something went wrong during packing: {e}", fg='red', bold=True)

if __name__ == "__main__":
    pack_ico()
