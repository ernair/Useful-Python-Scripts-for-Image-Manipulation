"""
Batch & Single Background Remover (Color to Alpha PNG/WebP Exporter via Click)
===============================================================================
Automates smooth background removal for a single image or an entire directory,
exporting the results as transparent PNG (default) or transparent WebP files.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_remove_bg.py <mode> <target_input> [options]

Required Arguments:
    <mode>          Background color to remove: 'black' (or '1') or 'white' (or '2').
    <target_input>  Single filename (e.g., logo.webp) OR 'all' for the whole folder.

Optional Flags:
    --webp          Save output as transparent WebP instead of PNG.
    -f, --force     Bypass the confirmation prompt for large batches (>5 files).
    -h, --help      Show the built-in help menu.

Examples:
    python batch_remove_bg.py black neon_logo.png
    python batch_remove_bg.py 1 all --webp
    python batch_remove_bg.py white all -f
"""

import os
import click
from PIL import Image

def remove_color_background(img, bg_color):
    """Applies a 'Color to Alpha' algorithm, making black or white
    backgrounds smoothly transparent.
    """
    rgba_img = img.convert("RGBA")
    pixels = rgba_img.getdata()
    new_pixels = []
    
    if bg_color in ('black', '1'):
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
                
    elif bg_color in ('white', '2'):
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
@click.argument('mode', type=click.Choice(['black', 'white', '1', '2'], case_sensitive=False))
@click.argument('target_input')
@click.option('--webp', is_flag=True, help='Save the transparent output as WebP instead of PNG.')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def clean_backgrounds(mode, target_input, webp, force):
    """Single & Bulk Transparent Background Remover.
    
    Removes solid black ('black' or '1') or white ('white' or '2') backgrounds 
    smoothly using a Color-to-Alpha pipeline and exports transparent PNG or WebP files.
    
    Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = []
    bg_mode = mode.lower()

    out_ext = ".webp" if webp else ".png"
    out_format = "WEBP" if webp else "PNG"

    if target_input.lower() == 'all':
        files_to_process = [
            f for f in os.listdir(current_dir) 
            if f.lower().endswith(valid_extensions) 
            and not f.lower().endswith('_transparent.png')
            and not f.lower().endswith('_transparent.webp')
        ]
        
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to process in: {current_dir}")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to process a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch conversion...")
        elif force:
            click.echo("Force flag (-f/--force) detected. Bypassing safety prompts...")
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        if not target_input.lower().endswith(valid_extensions):
            click.secho(f"Error: Unsupported file format. Supported: {', '.join(valid_extensions)}", fg='red', bold=True)
            return
        files_to_process = [target_input]

    color_label = "BLACK" if bg_mode in ('black', '1') else "WHITE"
    click.echo(f"\n--- Starting Background Removal (Color: {color_label}, Format: {out_format}) ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        out_path = f"{file_name_without_ext}_transparent{out_ext}"
        
        try:
            click.echo(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                transparent_img = remove_color_background(img, bg_mode)
                
                if webp:
                    transparent_img.save(out_path, format="WEBP", quality=90, method=6)
                else:
                    transparent_img.save(out_path, format="PNG")
                    
                click.secho(f"  -> Saved {out_format}: {out_path}", fg='cyan')
                success_count += 1
                
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully converted {success_count}/{len(files_to_process)} image(s) to transparent {out_format}.", fg='green', bold=True)

if __name__ == "__main__":
    clean_backgrounds()
