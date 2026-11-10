"""
Single Background Cleaner (Color to Alpha Utility via Click)
============================================================
Performs pure background removal on a single file and exports the result 
as a transparent PNG file.

It utilizes the 'click' library for clean argument parsing, automated validation, 
and native terminal coloring.

Prerequisites:
    pip install Pillow click

Usage:
    python remove_bg.py <mode> <image_path>
"""

import os
import sys
import click
from PIL import Image

def remove_color_background(img, mode):
    """Applies a 'Color to Alpha' algorithm, making black or white
    backgrounds smoothly transparent.
    """
    rgba_img = img.convert("RGBA")
    pixels = rgba_img.getdata()
    new_pixels = []
    
    if mode == 1:
        for item in pixels:
            r, g, b, a = item
            max_channel = max(r, g, b)
            if max_channel == 0:
                new_pixels.append((0, 0, 0, 0))
            else:
                alpha = max_channel
                new_r = int((r / max_channel) * 255)
                new_g = int((g / max_channel) * 255)
                new_b = int((b / max_channel) * 255)
                new_pixels.append((new_r, new_g, new_b, alpha))
                
    elif mode == 2:
        for item in pixels:
            r, g, b, a = item
            min_channel = min(r, g, b)
            if min_channel == 255:
                new_pixels.append((0, 0, 0, 0))
            else:
                alpha = 255 - min_channel
                new_r = int(((r - min_channel) / (255 - min_channel)) * 255)
                new_g = int(((g - min_channel) / (255 - min_channel)) * 255)
                new_b = int(((b - min_channel) / (255 - min_channel)) * 255)
                new_pixels.append((new_r, new_g, new_b, alpha))

    rgba_img.putdata(new_pixels)
    return rgba_img

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('mode', type=click.Choice(['1', '2']), callback=lambda c, p, v: int(v) if v else None)
@click.argument('image_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def clean_background(mode, image_path):
    """Single Background Cleaner.
    
    Removes solid black (1) or white (2) backgrounds smoothly from a single 
    target image and exports the result as a transparent PNG.
    """
    file_name_without_ext, _ = os.path.splitext(image_path)
    png_out_path = f"{file_name_without_ext}_transparent.png"

    try:
        click.echo(f"Processing '{image_path}'...")
        with Image.open(image_path) as img:
            transparent_img = remove_color_background(img, mode)
            transparent_img.save(png_out_path, format="PNG")
            click.secho(f"Success! Transparent PNG saved as: {png_out_path}", fg='green', bold=True)

    except Exception as e:
        click.secho(f"Something went wrong: {e}", fg='red', bold=True)

if __name__ == "__main__":
    clean_background()
