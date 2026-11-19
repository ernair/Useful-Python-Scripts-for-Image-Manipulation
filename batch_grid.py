"""
Batch Image Grid & Contact Sheet Generator (via Click)
======================================================
Combines all raster images in the current directory into a clean, uniform 
grid collage (contact sheet or sprite sheet). Supports custom column counts, 
cell sizes, pixel gaps, center-cropping, and flexible backgrounds (transparent, 
any CSS/hex color, colors.json presets, or a custom background image).

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_grid.py [options]

Examples:
    python batch_grid.py --cols 4 --size 300 --gap 20 --bg "#1A0033"
    python batch_grid.py -c 3 -s 400 -g 15 --bg wallpaper.jpg --crop
    python batch_grid.py -c 5 -s 128 -g 0 --bg transparent -o spritesheet.png
"""

import os
import math
import json
import click
from PIL import Image, ImageOps, ImageColor

def load_color_presets():
    """Loads custom color presets from 'colors.json' if available."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'colors.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k.strip().lower(): str(v).strip() for k, v in data.items() if isinstance(v, str)}
        except Exception:
            pass
    return {}

def create_grid_canvas(width, height, bg_spec, presets):
    """Creates the base RGBA canvas from 'transparent', a color/hex/preset, or an image file."""
    clean_bg = bg_spec.strip()
    lower_bg = clean_bg.lower()

    if lower_bg == 'transparent':
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Check if bg_spec points to an existing image file
    if os.path.isfile(clean_bg):
        try:
            with Image.open(clean_bg) as bg_img:
                bg_rgba = bg_img.convert("RGBA")
                # Scale and center-crop background image to fit the exact grid dimensions without stretching
                fitted_bg = ImageOps.fit(bg_rgba, (width, height), method=Image.Resampling.LANCZOS)
                return fitted_bg
        except Exception as e:
            raise click.BadParameter(f"Could not open background image '{clean_bg}': {e}")

    # Check colors.json presets or standard CSS/hex colors
    target_color = presets.get(lower_bg, clean_bg)
    try:
        rgb = ImageColor.getrgb(target_color)
        r, g, b = rgb[:3]
        return Image.new("RGBA", (width, height), (r, g, b, 255))
    except ValueError:
        raise click.BadParameter(f"Invalid background '{bg_spec}'. Use 'transparent', a hex/color name, or a valid image path.")

def format_cell_image(img, cell_size, crop_mode):
    """Resizes a single image to fit or fill a square cell of cell_size x cell_size."""
    rgba_img = img.convert("RGBA")
    if crop_mode:
        # Center-crop to fill the entire square cell edge-to-edge
        return ImageOps.fit(rgba_img, (cell_size, cell_size), method=Image.Resampling.LANCZOS)
    else:
        # Fit proportionally inside the square cell without cropping, centered on transparent tile
        rgba_img.thumbnail((cell_size, cell_size), Image.Resampling.LANCZOS)
        tile = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
        offset_x = (cell_size - rgba_img.width) // 2
        offset_y = (cell_size - rgba_img.height) // 2
        tile.paste(rgba_img, (offset_x, offset_y), rgba_img)
        return tile

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.option('-c', '--cols', type=click.IntRange(1, 50), default=4, show_default=True, help='Number of columns in the grid.')
@click.option('-s', '--size', type=click.IntRange(32, 4096), default=300, show_default=True, help='Width and height of each square cell in pixels.')
@click.option('-g', '--gap', type=click.IntRange(0, 500), default=20, show_default=True, help='Spacing between cells and outer margin in pixels.')
@click.option('-b', '--bg', default='transparent', show_default=True, help="Background: 'transparent', color/hex (e.g., '#1A0033'), preset name, or image path.")
@click.option('--crop', is_flag=True, help='Center-crop images to fill each square cell completely instead of fitting.')
@click.option('-o', '--output', default='grid_collage.png', show_default=True, help='Output filename (supports .png, .jpg, .webp).')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt when combining a large number of images (>25).')
def build_grid(cols, size, gap, bg, crop, output, force):
    """Image Grid & Contact Sheet Collage Generator.
    
    Scans all supported raster images in the current folder and arranges them 
    into a clean grid collage. Supports transparent, solid color/hex, or custom 
    image backgrounds.
    
    Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    
    out_abs = os.path.abspath(output)
    bg_abs = os.path.abspath(bg) if os.path.isfile(bg) else None
    
    # Gather all valid images, excluding the output file itself and any background image used
    files = tuple(
        sorted(
            f for f in os.listdir(current_dir)
            if f.lower().endswith(valid_extensions)
            and os.path.abspath(f) != out_abs
            and (bg_abs is None or os.path.abspath(f) != bg_abs)
            and not f.lower().startswith('grid_collage.')
        )
    )

    if not files:
        click.secho("No matching raster images found in this folder to build a grid.", fg='yellow')
        return

    total_images = len(files)
    if total_images > 25 and not force:
        click.secho(f"\n[WARNING] You are about to combine {total_images} images into a single grid.", fg='yellow', bold=True)
        if not click.confirm("Are you sure you want to proceed?"):
            click.echo("Operation cancelled by user.")
            return

    actual_cols = min(cols, total_images)
    rows = math.ceil(total_images / actual_cols)

    # Calculate exact canvas dimensions including outer margins and inner gaps
    canvas_w = gap + actual_cols * (size + gap)
    canvas_h = gap + rows * (size + gap)

    presets = load_color_presets()
    try:
        canvas = create_grid_canvas(canvas_w, canvas_h, bg, presets)
    except click.BadParameter as bp:
        click.secho(f"Error: {bp.format_message()}", fg='red', bold=True)
        return

    fit_mode_str = "Center-Crop" if crop else "Proportional Fit"
    click.echo(f"\n--- Building Grid Collage ({total_images} images | {actual_cols}x{rows} grid | {canvas_w}x{canvas_h} px | {fit_mode_str}) ---")

    placed_count = 0
    for idx, file_name in enumerate(files):
        row_idx = idx // actual_cols
        col_idx = idx % actual_cols
        
        pos_x = gap + col_idx * (size + gap)
        pos_y = gap + row_idx * (size + gap)
        
        try:
            with Image.open(file_name) as img:
                cell_img = format_cell_image(img, size, crop)
                canvas.paste(cell_img, (pos_x, pos_y), cell_img)
                placed_count += 1
        except Exception as e:
            click.secho(f"  -> Skipped '{file_name}': {e}", fg='yellow')

    if placed_count == 0:
        click.secho("Error: Could not process any images.", fg='red', bold=True)
        return

    _, out_ext = os.path.splitext(output)
    out_ext_lower = out_ext.lower()

    if os.path.exists(output):
        os.remove(output)

    try:
        if out_ext_lower in ('.jpg', '.jpeg'):
            # Flatten onto white if transparent background was chosen for a JPG output
            rgb_bg = Image.new("RGB", canvas.size, (255, 255, 255))
            rgb_bg.paste(canvas, (0, 0), canvas)
            rgb_bg.save(output, format="JPEG", quality=95)
        elif out_ext_lower == '.webp':
            canvas.save(output, format="WEBP", quality=90, method=6)
        else:
            canvas.save(output, format="PNG")
            
        click.secho(f"\nSuccess! Created '{output}' ({canvas_w}x{canvas_h} px) with {placed_count} image(s).", fg='green', bold=True)
    except Exception as e:
        click.secho(f"Failed to save output file '{output}': {e}", fg='red', bold=True)

if __name__ == "__main__":
    build_grid()
