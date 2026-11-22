"""
Batch & Single Image Quality Enhancer (via Click)
=================================================
Adjusts sharpness, contrast, brightness, and color saturation for a single 
image or an entire directory ('all') using Pillow's ImageEnhance engine while 
preserving alpha transparency.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_enhance.py <target_input> [options]

Examples:
    python batch_enhance.py icon.png --sharpness 1.4 --contrast 1.15
    python batch_enhance.py all -s 1.3 -c 1.1 --color 1.2
    python batch_enhance.py photo.jpg --brightness 1.1 --contrast 1.2
"""

import os
import click
from PIL import Image, ImageEnhance

def enhance_image(img, sharpness, contrast, brightness, color_sat):
    """Applies sharpness, contrast, brightness, and saturation adjustments while preserving alpha."""
    orig_rgba = img.convert("RGBA")
    r, g, b, alpha = orig_rgba.split()
    working_rgb = orig_rgba.convert("RGB")

    if color_sat != 1.0:
        working_rgb = ImageEnhance.Color(working_rgb).enhance(color_sat)
    if contrast != 1.0:
        working_rgb = ImageEnhance.Contrast(working_rgb).enhance(contrast)
    if brightness != 1.0:
        working_rgb = ImageEnhance.Brightness(working_rgb).enhance(brightness)
    if sharpness != 1.0:
        working_rgb = ImageEnhance.Sharpness(working_rgb).enhance(sharpness)

    final_rgba = working_rgb.convert("RGBA")
    final_rgba.putalpha(alpha)
    return final_rgba

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('-s', '--sharpness', type=click.FloatRange(0.0, 5.0), default=1.0, show_default=True, help='Sharpness factor (1.0 = original, >1.0 = sharper, <1.0 = blurred).')
@click.option('-c', '--contrast', type=click.FloatRange(0.0, 5.0), default=1.0, show_default=True, help='Contrast factor (1.0 = original, >1.0 = higher contrast).')
@click.option('-b', '--brightness', type=click.FloatRange(0.0, 5.0), default=1.0, show_default=True, help='Brightness factor (1.0 = original, >1.0 = brighter).')
@click.option('--color', 'color_sat', type=click.FloatRange(0.0, 5.0), default=1.0, show_default=True, help='Color saturation factor (1.0 = original, 0.0 = grayscale, >1.0 = vivid).')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt for large batches (more than 5 files).')
def process_enhance(target_input, sharpness, contrast, brightness, color_sat, force):
    """Single & Bulk Image Sharpness, Contrast, Brightness & Saturation Enhancer.
    
    Enhances visual clarity and punchiness for a single image or an entire 
    directory ('all') while preserving alpha transparency.
    """
    if sharpness == 1.0 and contrast == 1.0 and brightness == 1.0 and color_sat == 1.0:
        click.secho("Notice: All enhancement factors are at default (1.0). Specify at least one option (-s, -c, -b, or --color).", fg='yellow')
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = tuple()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            f for f in os.listdir(current_dir)
            if f.lower().endswith(valid_extensions)
            and '_enhanced.' not in f.lower()
        )
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to enhance.")
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to enhance a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch enhancement...")
        elif force:
            click.echo("Force flag (-f/--force) detected. Bypassing safety prompts...")
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        if not target_input.lower().endswith(valid_extensions):
            click.secho(f"Error: Unsupported file format. Supported: {', '.join(valid_extensions)}", fg='red', bold=True)
            return
        files_to_process = (target_input,)

    click.echo(f"\n--- Enhancing Images (Sharpness: {sharpness} | Contrast: {contrast} | Brightness: {brightness} | Color: {color_sat}) ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, orig_ext = os.path.splitext(file_name)
        orig_ext_lower = orig_ext.lower()
        
        if orig_ext_lower in ('.jpg', '.jpeg'):
            out_ext = '.jpg'
            out_path = f"{file_name_without_ext}_enhanced{out_ext}"
        elif orig_ext_lower == '.webp':
            out_ext = '.webp'
            out_path = f"{file_name_without_ext}_enhanced{out_ext}"
        elif orig_ext_lower == '.png':
            out_ext = '.png'
            out_path = f"{file_name_without_ext}_enhanced{out_ext}"
        else:
            out_ext = '.png'
            ext_tag = orig_ext_lower.lstrip('.')
            out_path = f"{file_name_without_ext}_{ext_tag}_enhanced{out_ext}"

        try:
            click.echo(f"Enhancing '{file_name}'...")
            with Image.open(file_name) as img:
                result_img = enhance_image(img, sharpness, contrast, brightness, color_sat)
                
                if os.path.exists(out_path):
                    os.remove(out_path)
                    
                if out_ext == '.jpg':
                    result_img.convert("RGB").save(out_path, format="JPEG", quality=95)
                elif out_ext == '.webp':
                    result_img.save(out_path, format="WEBP", quality=90, method=6)
                else:
                    result_img.save(out_path, format="PNG")
                    
                click.secho(f"  -> Saved: {out_path}", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to enhance '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully enhanced {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    process_enhance()
