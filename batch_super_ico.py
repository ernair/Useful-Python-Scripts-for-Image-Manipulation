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
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches of files (more than 5).')
@click.option('--png', is_flag=True, help='Additionally save the transparent images as standalone PNG files.')
def process_batch(mode, force, png):
    """Ultimate Bulk Icon Generator.
    
    Scans the current folder for ALL JPG, JPEG, and PNG images, removes solid 
    black (1) or white (2) backgrounds smoothly, and outputs Windows .ico files.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    
    # Scan for valid images, ignoring previously generated assets
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('.ico') and not f.lower().endswith('_transparent.png')]
    
    if not files:
        click.secho("No matching JPG or PNG images found in this folder.", fg='yellow')
        return

    click.echo(f"Found {len(files)} images to process in: {current_dir}")
    
    # Safety confirmation prompt managed elegantly
    CRITICAL_LIMIT = 5
    if len(files) > CRITICAL_LIMIT and not force:
        click.echo(f"\n[WARNING] You are about to process a large batch of images ({len(files)} files).")
        if not click.confirm("Are you sure you want to proceed?"):
            click.echo("Operation cancelled by user.")
            return
        click.echo("Proceeding with batch conversion...")
    elif force:
        click.echo("Force flag (-f) detected. Bypassing safety prompts...")

    click.echo("\n--- Starting Conversion ---")
    success_count = 0

    for file_name in files:
        file_name_without_ext, _ = os.path.splitext(file_name)
        ico_path = f"{file_name_without_ext}.ico"
        png_out_path = f"{file_name_without_ext}_transparent.png"
        
        try:
            click.echo(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                # 1. Remove background
                transparent_img = remove_color_background(img, mode)
                
                # 2. Save ICO (always done)
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                transparent_img.save(ico_path, format="ICO", sizes=icon_sizes)
                click.secho(f"  -> Saved successfully as: {ico_path}", fg='cyan')
                
                # 3. Save PNG (only if --png option flag is active)
                if png:
                    transparent_img.save(png_out_path, format="PNG")
                    click.secho(f"  -> Saved successfully as: {png_out_path}", fg='cyan')
                    
                success_count += 1
                
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nBatch processing finished! Successfully converted {success_count}/{len(files)} images.", fg='green', bold=True)

if __name__ == "__main__":
    process_batch()
