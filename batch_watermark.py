"""
Batch & Single Image Watermarker (Text & Logo Stamping via Click)
=================================================================
Applies customizable text or transparent image watermarks to a single image 
or an entire directory. Supports proportional scaling, edge margin control, 
opacity adjustment, and 5 anchor positions.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_watermark.py <target_input> [options]

Required Arguments:
    <target_input>  Single filename (e.g., wallpaper.jpg) OR 'all' for the whole folder.

Optional Flags:
    -t, --text      Text string to stamp as a watermark (e.g., "© My Name").
    -l, --logo      Path to a transparent PNG/WebP logo to use as a watermark.
    -p, --pos       Position: bottom-right (default), bottom-left, top-right, top-left, center.
    -s, --scale     Watermark width as a percentage of base image width (1-90, default: 15).
    -m, --margin    Margin from edges as a percentage of base image width (0-30, default: 3).
    -o, --opacity   Watermark opacity percentage (1-100, default: 70).
    -f, --force     Bypass the confirmation prompt for large batches (>5 files).
    -h, --help      Show the built-in help menu.

Examples:
    python batch_watermark.py wallpaper.jpg --text "© CyberArt 2026"
    python batch_watermark.py all --logo signature.png -p bottom-left -s 20 -o 80
    python batch_watermark.py all -t "DRAFT" -p center -s 50 -o 30 -f
"""

import os
import click
from PIL import Image, ImageDraw, ImageFont, ImageColor

def load_scalable_font(font_size):
    """Attempts to load a clean TrueType font on Windows/Linux/Mac, falling back safely."""
    font_candidates = [
        "arial.ttf",
        "segoeui.ttf",
        "calibri.ttf",
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf"
    ]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, font_size)
        except IOError:
            continue
    return ImageFont.load_default()

def create_text_watermark_layer(text, target_width, opacity, text_color="white"):
    """Renders crisp colored text with a subtle drop shadow onto a transparent RGBA layer."""
    try:
        rgb = ImageColor.getrgb(text_color)
    except ValueError:
        rgb = (255, 255, 255)  # Fallback to white if color name is invalid

    ref_size = 100
    ref_font = load_scalable_font(ref_size)
    
    dummy_img = Image.new("RGBA", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), text, font=ref_font)
    ref_w = max(1, bbox[2] - bbox[0])
    
    scaled_font_size = max(10, int(ref_size * (target_width / ref_w)))
    font = load_scalable_font(scaled_font_size)
    
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    shadow_offset = max(1, scaled_font_size // 20)
    layer_w = text_w + shadow_offset * 2
    layer_h = text_h + shadow_offset * 2
    
    txt_layer = Image.new("RGBA", (layer_w, layer_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    alpha_val = int(255 * (opacity / 100.0))
    shadow_alpha = int(alpha_val * 0.75)
    
    # Use a light shadow if the text is very dark, otherwise use a dark shadow
    is_dark = (rgb[0] + rgb[1] + rgb[2]) < 120
    shadow_rgb = (255, 255, 255) if is_dark else (0, 0, 0)
    
    draw.text((-bbox[0] + shadow_offset, -bbox[1] + shadow_offset), text, font=font, fill=(*shadow_rgb, shadow_alpha))
    draw.text((-bbox[0], -bbox[1]), text, font=font, fill=(rgb[0], rgb[1], rgb[2], alpha_val))
    
    return txt_layer


def prepare_logo_watermark_layer(logo_img, target_width, opacity):
    """Scales a logo image proportionally and adjusts its alpha opacity."""
    logo_rgba = logo_img.convert("RGBA")
    orig_w, orig_h = logo_rgba.size
    
    aspect_ratio = orig_h / orig_w
    target_height = max(1, int(target_width * aspect_ratio))
    
    resized_logo = logo_rgba.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    if opacity < 100:
        r, g, b, alpha = resized_logo.split()
        factor = opacity / 100.0
        alpha = alpha.point(lambda p: int(p * factor))
        resized_logo.putalpha(alpha)
        
    return resized_logo

def apply_watermark(base_img, wm_layer, position, margin_pct):
    """Composites the watermark layer onto the base image at the specified anchor."""
    base_rgba = base_img.convert("RGBA")
    base_w, base_h = base_rgba.size
    wm_w, wm_h = wm_layer.size
    
    margin_px = int(base_w * (margin_pct / 100.0))
    
    if position == 'top-left':
        x, y = margin_px, margin_px
    elif position == 'top-right':
        x, y = base_w - wm_w - margin_px, margin_px
    elif position == 'bottom-left':
        x, y = margin_px, base_h - wm_h - margin_px
    elif position == 'center':
        x, y = (base_w - wm_w) // 2, (base_h - wm_h) // 2
    else:  # bottom-right (default)
        x, y = base_w - wm_w - margin_px, base_h - wm_h - margin_px
        
    # Keep within bounds if watermark + margin exceeds image size
    x = max(0, min(x, base_w - wm_w))
    y = max(0, min(y, base_h - wm_h))
    
    canvas = base_rgba.copy()
    canvas.paste(wm_layer, (x, y), wm_layer)
    return canvas

# --- CLICK CLI CONFIGURATION ---


@click.command()
@click.argument('target_input')
@click.option('-t', '--text', default=None, help='Text string to stamp as a watermark (e.g., "© My Name").')
@click.option('-l', '--logo', type=click.Path(exists=True, file_okay=True, dir_okay=False), default=None, help='Path to a logo image to use as a watermark.')
@click.option('-p', '--pos', type=click.Choice(['bottom-right', 'bottom-left', 'top-right', 'top-left', 'center'], case_sensitive=False), default='bottom-right', show_default=True, help='Anchor position on the image.')
@click.option('-s', '--scale', type=click.IntRange(1, 90), default=15, show_default=True, help='Watermark width as % of base image width.')
@click.option('-m', '--margin', type=click.IntRange(0, 30), default=3, show_default=True, help='Edge margin as % of base image width.')
@click.option('-o', '--opacity', type=click.IntRange(1, 100), default=70, show_default=True, help='Watermark opacity percentage (1-100).')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
@click.option('-c', '--color', default='white', show_default=True, help='Text color name (e.g., cyan, red, black) or hex code (e.g., #FF0055).')
def stamp_watermarks(target_input, text, logo, pos, scale, margin, opacity, color, force):
    """Single & Bulk Image Watermarker.
    
    Adds a customizable text or logo watermark to a single image or an entire 
    directory ('all'). Supports proportional sizing, edge margins, and opacity control.
    """
    if not text and not logo:
        click.secho("Error: You must specify either --text (-t) or --logo (-l).", fg='red', bold=True)
        return
    if text and logo:
        click.secho("Error: Please choose either --text OR --logo, not both at the same time.", fg='red', bold=True)
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = []
    pos = pos.lower()
    logo_abs_path = os.path.abspath(logo) if logo else None

    if target_input.lower() == 'all':
        for f in os.listdir(current_dir):
            lower_f = f.lower()
            if not lower_f.endswith(valid_extensions):
                continue
            if '_watermarked.' in lower_f:
                continue
            if logo_abs_path and os.path.abspath(f) == logo_abs_path:
                continue
            files_to_process.append(f)
            
        if not files_to_process:
            click.secho("No matching raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to watermark.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to watermark a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch watermarking...")
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

    wm_type = f"Text ('{text}')" if text else f"Logo ('{logo}')"
    click.echo(f"\n--- Starting Watermarking ({wm_type} | Pos: {pos} | Size: {scale}% | Margin: {margin}% | Opacity: {opacity}%) ---")
    success_count = 0

    opened_logo = Image.open(logo) if logo else None

    try:
        for file_name in files_to_process:
            file_name_without_ext, orig_ext = os.path.splitext(file_name)
            orig_ext_lower = orig_ext.lower()
            
            if orig_ext_lower in ('.jpg', '.jpeg'):
                out_ext = '.jpg'
            elif orig_ext_lower == '.webp':
                out_ext = '.webp'
            else:
                out_ext = '.png'
                
            out_path = f"{file_name_without_ext}_watermarked{out_ext}"
            
            try:
                click.echo(f"Watermarking '{file_name}'...")
                with Image.open(file_name) as base_img:
                    target_wm_width = max(10, int(base_img.width * (scale / 100.0)))
                    
                    if text:
                        wm_layer = create_text_watermark_layer(text, target_wm_width, opacity, color)
                    else:
                        wm_layer = prepare_logo_watermark_layer(opened_logo, target_wm_width, opacity)
                        
                    result_img = apply_watermark(base_img, wm_layer, pos, margin)
                    
                    if out_ext == '.jpg':
                        rgb_canvas = Image.new("RGB", result_img.size, (255, 255, 255))
                        rgb_canvas.paste(result_img, (0, 0), result_img)
                        rgb_canvas.save(out_path, format="JPEG", quality=95)
                    elif out_ext == '.webp':
                        result_img.save(out_path, format="WEBP", quality=90, method=6)
                    else:
                        result_img.save(out_path, format="PNG")
                        
                    click.secho(f"  -> Saved: {out_path}", fg='cyan')
                    success_count += 1
                    
            except Exception as e:
                click.secho(f"  -> Failed to watermark '{file_name}': {e}", fg='red', bold=True)
    finally:
        if opened_logo:
            opened_logo.close()

    click.secho(f"\nFinished! Successfully watermarked {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    stamp_watermarks()
