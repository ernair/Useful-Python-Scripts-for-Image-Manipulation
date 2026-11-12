"""
Batch & Single ICO Generator (Optional Color to Alpha + Multi-Res ICO via Click)
================================================================================
Converts a single image or an entire folder into multi-resolution Windows Icons (.ico).
Optionally removes solid black or white backgrounds smoothly using a Color-to-Alpha 
pipeline before packing.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_ico.py <target_input> [options]

Required Arguments:
    <target_input>  Single filename (e.g., logo.png) OR 'all' for the whole folder.

Optional Flags:
    -b, --bg        Background color to remove: 'black' or 'white' (default: none).
    --png           Also save the processed result as a standalone PNG file.
    -f, --force     Bypass the confirmation prompt for large batches (>5 files).
    -h, --help      Show the built-in help menu.

Examples:
    python batch_ico.py ready_transparent_logo.png
    python batch_ico.py neon_icon.webp -b black
    python batch_ico.py all -b white --png -f
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
    
    if bg_color == 'black':
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
                
    elif bg_color == 'white':
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
@click.argument('target_input')
@click.option('-b', '--bg', type=click.Choice(['black', 'white'], case_sensitive=False), default=None, help="Optional background color to remove ('black' or 'white').")
@click.option('--png', is_flag=True, help='Additionally save the processed images as standalone PNG files.')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def generate_ico(target_input, bg, png, force):
    """Single & Bulk Windows Icon (.ico) Generator.
    
    Packs images into a multi-resolution .ico container. Optionally removes solid 
    black or white backgrounds smoothly before packing.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = []
    bg_mode = bg.lower() if bg else None

    if target_input.lower() == 'all':
        files_to_process = [
            f for f in os.listdir(current_dir) 
            if f.lower().endswith(valid_extensions) 
            and not f.lower().endswith('_transparent.png')
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

    bg_info = f"Remove {bg_mode.upper()}" if bg_mode else "None (Keep original)"
    click.echo(f"\n--- Starting ICO Generation (Background Removal: {bg_info}) ---")
    success_count = 0
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        ico_path = f"{file_name_without_ext}.ico"
        png_out_path = f"{file_name_without_ext}_transparent.png"
        
        try:
            click.echo(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                if bg_mode:
                    processed_img = remove_color_background(img, bg_mode)
                else:
                    processed_img = img.convert("RGBA")
                
                processed_img.save(ico_path, format="ICO", sizes=icon_sizes)
                click.secho(f"  -> Saved ICO: {ico_path}", fg='cyan')
                
                if png:
                    processed_img.save(png_out_path, format="PNG")
                    click.secho(f"  -> Saved PNG: {png_out_path}", fg='cyan')
                    
                success_count += 1
                
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully converted {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    generate_ico()
