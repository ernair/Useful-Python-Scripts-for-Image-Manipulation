"""
Batch Image Overlay Compositor (Two-Way Single & Bulk Merger via Click)
=======================================================================
This command-line utility centers a foreground image onto a base background image.
Supports 'all' in EITHER position:
  - 'all base.png'  -> Centers every image in the folder onto one base image.
  - 'logo.png all'  -> Centers one foreground logo onto every image in the folder.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_overlay.py <foreground_input> <base_input> [options]

Examples:
    python batch_overlay.py all frame.png -l -s 20
    python batch_overlay.py logo.png all -l -s 50 --format webp
"""

import os
import click
from PIL import Image

def composite_images(fg_img, base_img, scale_pct, lock_to_base):
    """Scales the foreground image and pastes it dead-center onto the base image."""
    base_rgba = base_img.convert("RGBA")
    fg_rgba = fg_img.convert("RGBA")
    
    base_w, base_h = base_rgba.size
    fg_w, fg_h = fg_rgba.size
    
    # Calculate scaling factor (e.g., scale_pct 20 -> keep 80% of size)
    keep_ratio = (100 - scale_pct) / 100.0
    
    if lock_to_base:
        # Fit foreground proportionally within base dimensions first, then apply shrink %
        fit_ratio = min(base_w / fg_w, base_h / fg_h)
        target_w = max(1, int(fg_w * fit_ratio * keep_ratio))
        target_h = max(1, int(fg_h * fit_ratio * keep_ratio))
    else:
        # Shrink relative to foreground's own original dimensions
        target_w = max(1, int(fg_w * keep_ratio))
        target_h = max(1, int(fg_h * keep_ratio))
        
    if target_w != fg_w or target_h != fg_h:
        fg_rgba = fg_rgba.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
    # Calculate dead-center coordinates
    offset_x = (base_w - target_w) // 2
    offset_y = (base_h - target_h) // 2
    
    # Paste using fg_rgba as its own alpha transparency mask
    canvas = base_rgba.copy()
    canvas.paste(fg_rgba, (offset_x, offset_y), fg_rgba)
    return canvas

def save_output(result_img, output_path, out_format):
    """Saves the composited image in the chosen raster format."""
    if out_format == 'jpg':
        rgb_canvas = Image.new("RGB", result_img.size, (255, 255, 255))
        rgb_canvas.paste(result_img, (0, 0), result_img)
        rgb_canvas.save(output_path, format="JPEG", quality=95)
    elif out_format == 'webp':
        result_img.save(output_path, format="WEBP", quality=90, method=6)
    else:
        result_img.save(output_path, format="PNG")

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('foreground_input')
@click.argument('base_input')
@click.option('-s', '--scale', type=click.IntRange(0, 99), default=0, show_default=True, help='Percentage to shrink the foreground image (0-99).')
@click.option('-l', '--lock', is_flag=True, help='Scale relative to the base image dimensions instead of original foreground size.')
@click.option('--format', 'out_format', type=click.Choice(['png', 'jpg', 'webp'], case_sensitive=False), default='png', show_default=True, help='Output raster image format.')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def overlay_images(foreground_input, base_input, scale, lock, out_format, force):
    """Two-Way Image Overlay Compositor.
    
    Places a foreground image dead-center onto a base background image.
    Use 'all' as FOREGROUND_INPUT or BASE_INPUT for batch processing.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    current_dir = os.getcwd()
    out_format = out_format.lower()
    out_ext = f".{out_format}"

    fg_is_all = foreground_input.lower() == 'all'
    base_is_all = base_input.lower() == 'all'

    # Prevent 'all all' explosion
    if fg_is_all and base_is_all:
        click.secho("Error: Both arguments cannot be 'all'. Specify at least one concrete image file.", fg='red', bold=True)
        return

    # --- MODE 1: ALL FOREGROUNDS ONTO ONE BASE ---
    if fg_is_all:
        if not os.path.exists(base_input):
            click.secho(f"Error: Base file '{base_input}' was not found.", fg='red', bold=True)
            return
            
        base_abs = os.path.abspath(base_input)
        files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and '_merged.' not in f.lower() and os.path.abspath(f) != base_abs]
        
        if not files:
            click.secho("No matching foreground images found in this folder.", fg='yellow')
            return

        if len(files) > 5 and not force:
            click.secho(f"\n[WARNING] You are about to process {len(files)} foreground images.", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled.")
                return

        click.echo(f"\n--- Compositing {len(files)} foregrounds onto '{base_input}' ---")
        success = 0
        with Image.open(base_input) as base_img:
            for f in files:
                name_no_ext, _ = os.path.splitext(f)
                out_path = f"{name_no_ext}_merged{out_ext}"
                try:
                    with Image.open(f) as fg_img:
                        res = composite_images(fg_img, base_img, scale, lock)
                        save_output(res, out_path, out_format)
                        click.secho(f"  -> Saved: {out_path}", fg='cyan')
                        success += 1
                except Exception as e:
                    click.secho(f"  -> Failed '{f}': {e}", fg='red')
        click.secho(f"\nFinished! Successfully composited {success}/{len(files)} image(s).", fg='green', bold=True)

    # --- MODE 2: ONE FOREGROUND ONTO ALL BASES ---
    elif base_is_all:
        if not os.path.exists(foreground_input):
            click.secho(f"Error: Foreground file '{foreground_input}' was not found.", fg='red', bold=True)
            return
            
        fg_abs = os.path.abspath(foreground_input)
        files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and '_merged.' not in f.lower() and os.path.abspath(f) != fg_abs]
        
        if not files:
            click.secho("No matching base images found in this folder.", fg='yellow')
            return

        if len(files) > 5 and not force:
            click.secho(f"\n[WARNING] You are about to stamp '{foreground_input}' onto {len(files)} base images.", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled.")
                return

        click.echo(f"\n--- Stamping '{foreground_input}' onto {len(files)} base images ---")
        success = 0
        with Image.open(foreground_input) as fg_img:
            for f in files:
                name_no_ext, _ = os.path.splitext(f)
                out_path = f"{name_no_ext}_merged{out_ext}"
                try:
                    with Image.open(f) as base_img:
                        res = composite_images(fg_img, base_img, scale, lock)
                        save_output(res, out_path, out_format)
                        click.secho(f"  -> Saved: {out_path}", fg='cyan')
                        success += 1
                except Exception as e:
                    click.secho(f"  -> Failed '{f}': {e}", fg='red')
        click.secho(f"\nFinished! Successfully composited {success}/{len(files)} image(s).", fg='green', bold=True)

    # --- MODE 3: SINGLE FOREGROUND ONTO SINGLE BASE ---
    else:
        if not os.path.exists(foreground_input) or not os.path.exists(base_input):
            click.secho("Error: One or both specified image files were not found.", fg='red', bold=True)
            return
            
        name_no_ext, _ = os.path.splitext(foreground_input)
        out_path = f"{name_no_ext}_merged{out_ext}"
        try:
            with Image.open(foreground_input) as fg_img, Image.open(base_input) as base_img:
                res = composite_images(fg_img, base_img, scale, lock)
                save_output(res, out_path, out_format)
                click.secho(f"Success! Saved as: {out_path}", fg='green', bold=True)
        except Exception as e:
            click.secho(f"Error during compositing: {e}", fg='red', bold=True)

if __name__ == "__main__":
    overlay_images()
