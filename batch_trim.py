"""
Batch & Single Smart Image Trimmer & Scaler (via Click)
=======================================================
Trims excess margins around an object (transparent, black, or white background) 
or crops a fixed percentage from the edges, with options to keep a uniform 
padding margin, force a 1:1 square aspect ratio, and upscale/restore back 
to the original image dimensions without distortion.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_trim.py <target_input> [options]

Examples:
    python batch_trim.py icon.png --auto --bg black --padding 5 --restore-size
    python batch_trim.py logo.png --auto --bg transparent -p 5 -r
    python batch_trim.py all --auto --bg black -p 3 -r
    python batch_trim.py photo.jpg --percent 15 --restore-size
"""

import os
import click
from PIL import Image, ImageChops

def get_auto_bbox(img, bg_mode, tolerance=12):
    """Finds the bounding box of non-background content with slight noise tolerance."""
    rgba = img.convert("RGBA")
    
    if bg_mode == 'transparent':
        alpha = rgba.getchannel('A')
        mask = alpha.point(lambda p: 255 if p > tolerance else 0)
        return mask.getbbox()
    else:
        rgb = rgba.convert("RGB")
        bg_color = (0, 0, 0) if bg_mode == 'black' else (255, 255, 255)
        bg_img = Image.new("RGB", rgb.size, bg_color)
        
        diff = ImageChops.difference(rgb, bg_img)
        gray_diff = diff.convert("L")
        mask = gray_diff.point(lambda p: 255 if p > tolerance else 0)
        return mask.getbbox()

def trim_and_process(img, auto_mode, bg_mode, percent, padding_pct, force_square, restore_size):
    """Crops the image intelligently, adds optional padding, and optionally restores original size.
    Returns None if --auto finds no excess background border to trim.
    """
    orig_w, orig_h = img.size
    orig_aspect = orig_w / float(orig_h)
    rgba_img = img.convert("RGBA")
    
    if auto_mode:
        bbox = get_auto_bbox(rgba_img, bg_mode)
        if not bbox or bbox == (0, 0, orig_w, orig_h):
            return None
            
        left, top, right, bottom = bbox
        obj_w = right - left
        obj_h = bottom - top
        
        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0
        
        if restore_size:
            if (obj_w / float(obj_h)) > orig_aspect:
                crop_w = float(obj_w)
                crop_h = crop_w / orig_aspect
            else:
                crop_h = float(obj_h)
                crop_w = crop_h * orig_aspect
        elif force_square:
            side = max(obj_w, obj_h)
            crop_w = float(side)
            crop_h = float(side)
        else:
            crop_w = float(obj_w)
            crop_h = float(obj_h)
            
        if padding_pct > 0:
            pad_w = crop_w * (padding_pct / 100.0)
            pad_h = crop_h * (padding_pct / 100.0)
            crop_w += pad_w * 2
            crop_h += pad_h * 2
            
        new_left = int(round(cx - crop_w / 2.0))
        new_top = int(round(cy - crop_h / 2.0))
        new_right = int(round(cx + crop_w / 2.0))
        new_bottom = int(round(cy + crop_h / 2.0))
        
        if bg_mode == 'black':
            fill_rgba = (0, 0, 0, 255)
        elif bg_mode == 'white':
            fill_rgba = (255, 255, 255, 255)
        else:
            fill_rgba = (0, 0, 0, 0)
            
        canvas_w = max(1, new_right - new_left)
        canvas_h = max(1, new_bottom - new_top)
        cropped = Image.new("RGBA", (canvas_w, canvas_h), fill_rgba)
        
        src_left = max(0, new_left)
        src_top = max(0, new_top)
        src_right = min(orig_w, new_right)
        src_bottom = min(orig_h, new_bottom)
        
        if src_right > src_left and src_bottom > src_top:
            part = rgba_img.crop((src_left, src_top, src_right, src_bottom))
            paste_x = src_left - new_left
            paste_y = src_top - new_top
            cropped.paste(part, (paste_x, paste_y))
            
    else:
        trim_x = int(round(orig_w * (percent / 100.0)))
        trim_y = int(round(orig_h * (percent / 100.0)))
        
        new_left = trim_x
        new_top = trim_y
        new_right = max(new_left + 1, orig_w - trim_x)
        new_bottom = max(new_top + 1, orig_h - trim_y)
        cropped = rgba_img.crop((new_left, new_top, new_right, new_bottom))

    if restore_size:
        cropped = cropped.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
        
    return cropped

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('--auto', 'auto_mode', is_flag=True, help='Automatically detect object bounds and trim excess background.')
@click.option('--percent', type=click.IntRange(1, 45), default=None, help='Trim a fixed percentage (1-45%) from all edges.')
@click.option('-b', '--bg', type=click.Choice(['black', 'white', 'transparent'], case_sensitive=False), default='black', show_default=True, help='Background type to trim in --auto mode.')
@click.option('-p', '--padding', type=click.IntRange(0, 50), default=5, show_default=True, help='Extra breathing room margin (%) to keep around object in --auto mode.')
@click.option('--square', is_flag=True, help='Force trimmed region to a 1:1 square (ignored if --restore-size is used).')
@click.option('-r', '--restore-size', is_flag=True, help='Scale the trimmed result back to the original image dimensions.')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt for large batches (more than 5 files).')
def trim_images(target_input, auto_mode, percent, bg, padding, square, restore_size, force):
    """Smart Image Trimmer & Size Restorer.
    
    Trims excess margins around an icon/object (--auto) or crops a fixed 
    percentage from edges (--percent), keeping a clean margin (--padding) and 
    optionally scaling back to the original dimensions (--restore-size).
    
    Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.
    """
    if not auto_mode and percent is None:
        click.secho("Error: Specify either --auto (for smart background trimming) or --percent <1-45>.", fg='red', bold=True)
        return
    if auto_mode and percent is not None:
        click.secho("Error: Choose either --auto OR --percent, not both at the same time.", fg='red', bold=True)
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = tuple()
    bg_mode = bg.lower()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            f for f in os.listdir(current_dir)
            if f.lower().endswith(valid_extensions)
            and '_trimmed.' not in f.lower()
        )
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to trim.")
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to trim a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch trimming...")
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

    mode_desc = f"Auto-Trim (BG: {bg_mode}, Padding: {padding}%)" if auto_mode else f"Percent Crop ({percent}%)"
    restore_desc = "Yes (Restore original px)" if restore_size else "No (Keep cropped px)"
    click.echo(f"\n--- Starting Image Trimming ({mode_desc} | Restore Size: {restore_desc}) ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, orig_ext = os.path.splitext(file_name)
        orig_ext_lower = orig_ext.lower()
        
        if orig_ext_lower in ('.jpg', '.jpeg'):
            out_ext = '.jpg'
            out_path = f"{file_name_without_ext}_trimmed{out_ext}"
        elif orig_ext_lower == '.webp':
            out_ext = '.webp'
            out_path = f"{file_name_without_ext}_trimmed{out_ext}"
        elif orig_ext_lower == '.png':
            out_ext = '.png'
            out_path = f"{file_name_without_ext}_trimmed{out_ext}"
        else:
            out_ext = '.png'
            ext_tag = orig_ext_lower.lstrip('.')
            out_path = f"{file_name_without_ext}_{ext_tag}_trimmed{out_ext}"
            
        try:
            click.echo(f"Trimming '{file_name}'...")
            with Image.open(file_name) as img:
                result_img = trim_and_process(img, auto_mode, bg_mode, percent, padding, square, restore_size)
                
                if result_img is None:
                    click.secho(f"  -> Skipped '{file_name}': No excess background border found to trim.", fg='yellow')
                    continue
                
                if os.path.exists(out_path):
                    os.remove(out_path)
                    
                if out_ext == '.jpg':
                    rgb_canvas = Image.new("RGB", result_img.size, (0, 0, 0) if bg_mode == 'black' else (255, 255, 255))
                    rgb_canvas.paste(result_img, (0, 0), result_img)
                    rgb_canvas.save(out_path, format="JPEG", quality=95)
                elif out_ext == '.webp':
                    result_img.save(out_path, format="WEBP", quality=90, method=6)
                else:
                    result_img.save(out_path, format="PNG")
                    
                click.secho(f"  -> Saved: {out_path} ({result_img.width}x{result_img.height} px)", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to trim '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully trimmed {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    trim_images()
