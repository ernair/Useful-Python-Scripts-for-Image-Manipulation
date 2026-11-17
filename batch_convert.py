"""
Batch & Single Raster Image Format Converter (via Click)
========================================================
Converts a single raster image or an entire directory between popular raster 
formats: PNG, JPG, WebP, BMP, TIFF, and GIF.

Automatically handles alpha transparency flattening onto a solid white (default) 
or black background when converting to formats that do not support transparency 
(such as JPG or BMP).

Prerequisites:
    pip install Pillow click

Usage:
    python batch_convert.py <target_input> <target_format> [options]

Required Arguments:
    <target_input>   Single filename (e.g., image.webp) OR 'all' for the whole folder.
    <target_format>  Target format: png, jpg, webp, bmp, tiff, or gif.

Optional Flags:
    -b, --bg         Background fill color ('white' or 'black') when flattening 
                     transparency for JPG/BMP (default: white).
    -q, --quality    Compression quality (1-100) for JPG and WebP outputs (default: 90).
    -f, --force      Bypass the confirmation prompt for large batches (>5 files).
    -h, --help       Show the built-in help menu.

Examples:
    python batch_convert.py neon_logo.png jpg --bg black
    python batch_convert.py all webp -q 85
    python batch_convert.py all png -f
"""

import os
import click
from PIL import Image

def prepare_image_for_format(img, target_format, bg_color):
    """Adjusts color modes and flattens transparency if the target format requires it."""
    # Formats that do NOT support alpha transparency
    no_alpha_formats = ('jpg', 'jpeg', 'bmp')
    
    if target_format in no_alpha_formats:
        # Check if the image has transparency
        has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        if has_alpha:
            fill_rgb = (0, 0, 0) if bg_color == 'black' else (255, 255, 255)
            background = Image.new("RGB", img.size, fill_rgb)
            rgba_img = img.convert("RGBA")
            background.paste(rgba_img, (0, 0), rgba_img)
            return background
        return img.convert("RGB")
        
    # Formats that DO support transparency (png, webp, tiff, gif)
    if img.mode in ('RGBA', 'LA', 'P'):
        return img.convert("RGBA")
    return img.convert("RGB")

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.argument('target_format', type=click.Choice(['png', 'jpg', 'webp', 'bmp', 'tiff', 'gif'], case_sensitive=False))
@click.option('-b', '--bg', type=click.Choice(['white', 'black'], case_sensitive=False), default='white', show_default=True, help='Background color when flattening transparency for JPG/BMP.')
@click.option('-q', '--quality', type=click.IntRange(1, 100), default=90, show_default=True, help='Compression quality (1-100) for JPG and WebP outputs.')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def convert_images(target_input, target_format, bg, quality, force):
    """Single & Bulk Raster Format Converter.
    
    Converts raster images between PNG, JPG, WebP, BMP, TIFF, and GIF formats.
    Automatically flattens transparency onto a white or black background for JPG/BMP.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = []
    
    out_format = target_format.lower()
    bg_color = bg.lower()

    # Determine matching target extensions to skip already converted files in 'all' mode
    skip_exts = ('.jpg', '.jpeg') if out_format == 'jpg' else ('.tiff', '.tif') if out_format == 'tiff' else (f'.{out_format}',)

    if target_input.lower() == 'all':
        for f in os.listdir(current_dir):
            lower_f = f.lower()
            if lower_f.endswith(valid_extensions) and not lower_f.endswith(skip_exts):
                files_to_process.append(f)
                
        if not files_to_process:
            click.secho(f"No raster images found that need conversion to {out_format.upper()}.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to convert to {out_format.upper()}.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to convert a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
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

    click.echo(f"\n--- Starting Format Conversion (Target: {out_format.upper()}, Transparency Fill: {bg_color.upper()}) ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        out_path = f"{file_name_without_ext}.{out_format}"
        
        # Prevent overwriting if single file already has the exact same extension
        if os.path.abspath(file_name) == os.path.abspath(out_path):
            click.secho(f"  -> Skipped '{file_name}': Already in {out_format.upper()} format.", fg='yellow')
            continue
            
        try:
            click.echo(f"Converting '{file_name}' -> '{out_path}'...")
            with Image.open(file_name) as img:
                prepared_img = prepare_image_for_format(img, out_format, bg_color)
                
                if out_format == 'jpg':
                    prepared_img.save(out_path, format="JPEG", quality=quality)
                elif out_format == 'webp':
                    prepared_img.save(out_path, format="WEBP", quality=quality, method=6)
                elif out_format == 'tiff':
                    prepared_img.save(out_path, format="TIFF")
                else:
                    prepared_img.save(out_path, format=out_format.upper())
                    
                click.secho(f"  -> Saved successfully: {out_path}", fg='cyan')
                success_count += 1
                
        except Exception as e:
            click.secho(f"  -> Failed to convert '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully converted {success_count}/{len(files_to_process)} image(s) to {out_format.upper()}.", fg='green', bold=True)

if __name__ == "__main__":
    convert_images()
