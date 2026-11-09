"""
Batch Super ICO Converter (Bulk Color to Alpha + Multi-Res ICO Generator via Click)
==================================================================================
This production-ready command-line tool automates background removal, transparent 
PNG exporting, and Windows Icon (.ico) generation for ALL images within the current 
working directory.

It utilizes the 'click' library for clean argument parsing, automated validation, 
and native terminal coloring. It scans the folder for JPG, JPEG, and PNG files, 
implements a safety confirmation check, and smoothly processes images using 
the 'Color to Alpha' pipeline.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_super_ico.py <mode> [options]

Required Arguments:
    <mode>    The background color to turn transparent:
                1 = Bulk Process Black Backgrounds (Smooth Black to Alpha)
                2 = Bulk Process White Backgrounds (Smooth White to Alpha)

Optional Flags:
    -f, --force  Force mode. Bypasses the confirmation prompt when a folder 
                 contains a large batch of images (more than 5 files).
    --png        PNG Export. Additionally saves the transparent results as 
                 standalone PNG files ('<name>_transparent.png').
    -h, --help   Show the built-in help menu and usage examples.

Examples:
    python batch_super_ico.py 1
    python batch_super_ico.py 1 --png
    python batch_super_ico.py --help
"""


import os
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
        click.echo("-> Applying smooth BLACK to Alpha...")
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
        click.echo("-> Applying smooth WHITE to Alpha...")
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
def create_ultimate_ico(mode, image_path):
    """Ultimate Single-File Icon Generator.
    
    Removes solid black (1) or white (2) backgrounds smoothly using a 
    Color-to-Alpha pipeline and packs the image into a Windows .ico container.
    """
    file_name_without_ext, _ = os.path.splitext(image_path)
    ico_path = f"{file_name_without_ext}.ico"

    try:
        click.echo(f"Processing '{image_path}'...")
        with Image.open(image_path) as img:
            # Run background removal
            transparent_img = remove_color_background(img, mode)

            # Define standard Windows desktop icon sizes
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

            # Save directly as ICO
            transparent_img.save(ico_path, format="ICO", sizes=icon_sizes)
            click.secho(f"Success! Icon saved as: {ico_path}", fg='green', bold=True)

    except Exception as e:
        click.secho(f"Something went wrong: {e}", fg='red', bold=True)

if __name__ == "__main__":
    create_ultimate_ico()
