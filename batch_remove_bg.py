"""
Batch PNG Background Remover (Bulk Color to Alpha Tool via Click)
==================================================================
This lightweight command-line utility automates the process of removing solid 
backgrounds from ALL images within the current working directory, exporting the 
results strictly as transparent PNG files.

It utilizes the 'click' library for clean argument parsing, automated validation, 
and native terminal coloring. It scans the folder for JPG, JPEG, and PNG files, 
implements a safety confirmation check, and smoothly processes images using 
the 'Color to Alpha' pipeline.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_remove_bg.py <mode> [options]
"""

import os
import sys
import click
from PIL import Image

def remove_color_background(img, mode):
    """Applies a 'Color to Alpha' algorithm, making black or white
    backgrounds smoothly transparent and returning an RGBA PNG image.
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
def process_batch(mode, force):
    """Ultimate Bulk PNG Background Remover.
    
    Scans the current folder for ALL JPG, JPEG, and PNG images, removes solid 
    black (1) or white (2) backgrounds smoothly, and exports transparent PNGs.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    
    # Scan for valid images, ignoring previously generated transparent assets
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('_transparent.png')]
    
    if not files:
        click.secho("No matching JPG or PNG images found in this folder.", fg='yellow')
        return

    click.echo(f"Found {len(files)} images to process in: {current_dir}")
    
    # Safety confirmation prompt managed elegantly via Click
    CRITICAL_LIMIT = 5
    if len(files) > CRITICAL_LIMIT and not force:
        click.secho(f"\n[WARNING] You are about to remove backgrounds from a large batch ({len(files)} files).", fg='yellow', bold=True)
        if not click.confirm("Are you sure you want to proceed?"):
            click.echo("Operation cancelled by user.")
            return
        click.echo("Proceeding with batch transparency conversion...")
    elif force:
        click.echo("Force flag (-f/--force) detected. Bypassing safety prompts...")

    click.echo("\n--- Starting PNG Background Removal ---")
    success_count = 0

    for file_name in files:
        file_name_without_ext, _ = os.path.splitext(file_name)
        png_out_path = f"{file_name_without_ext}_transparent.png"
        
        try:
            click.echo(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                # Remove background and save purely as a transparent PNG
                transparent_img = remove_color_background(img, mode)
                transparent_img.save(png_out_path, format="PNG")
                click.secho(f"  -> Saved successfully as: {png_out_path}", fg='cyan')
                success_count += 1
                
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nBatch processing finished! Successfully converted {success_count}/{len(files)} images to transparent PNG.", fg='green', bold=True)

if __name__ == "__main__":
    process_batch()
