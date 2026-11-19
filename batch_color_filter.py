"""
Batch & Single Color Filter (Monochrome Tint & Cyberpunk Duotone via Click)
===========================================================================
Applies creative color grading to a single image or an entire directory.
Loads and manages custom color presets in an external 'colors.json' file and 
supports single-color monochrome tinting, special modes (grayscale, sepia, 
bitmap, lineart), and two-tone Cyberpunk duotone mapping while preserving alpha.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_color_filter.py <target_input> [options]

Examples:
    python batch_color_filter.py --list-colors
    python batch_color_filter.py --add-color lava "#FF3300"
    python batch_color_filter.py icon.png --tint lava
    python batch_color_filter.py all --duotone deepviolet neon -i 85
"""

import os
import json
import click
from PIL import Image, ImageOps, ImageColor

def get_json_path():
    """Returns the absolute path to 'colors.json' located next to the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'colors.json')

def load_color_presets():
    """Loads custom color presets from 'colors.json' located next to the script."""
    default_presets = {
        'cyberpunk': '#FF0080',
        'neon': '#00FFC8',
        'matrix': '#00FF41',
        'inferno': '#A020F0'
    }
    json_path = get_json_path()
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                loaded = {k.strip().lower(): str(v).strip() for k, v in data.items() if isinstance(v, str)}
                if loaded:
                    return loaded
        except Exception as e:
            click.secho(f"[Warning] Could not read colors.json ({e}). Using built-in defaults.", fg='yellow')
            
    return default_presets

def save_color_preset(name, color_val):
    """Validates a color string, converts it to #RRGGBB hex, and saves it to colors.json."""
    clean_name = name.strip().lower()
    if not clean_name:
        raise click.BadParameter("Color preset name cannot be empty.")
        
    try:
        rgb = ImageColor.getrgb(color_val.strip())
        # Convert to clean uppercase #RRGGBB format (ignoring alpha if 4-tuple)
        r, g, b = rgb[:3]
        hex_code = f"#{r:02X}{g:02X}{b:02X}"
    except ValueError:
        raise click.BadParameter(f"Invalid color value '{color_val}'. Use a valid hex code (e.g., #FF3300) or CSS color name.")

    presets = load_color_presets()
    existed = clean_name in presets
    presets[clean_name] = hex_code
    
    json_path = get_json_path()
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(presets, f, indent=4)
        
    return clean_name, hex_code, existed

def parse_color_safe(color_str, presets):
    """Converts a preset name, standard color name, or hex string into an RGB tuple."""
    clean_str = color_str.strip().lower()
    target_val = presets.get(clean_str, color_str)
    try:
        return ImageColor.getrgb(target_val)
    except ValueError:
        raise click.BadParameter(f"Invalid color '{color_str}'. Use --list-colors, standard names (red, cyan), or hex codes (#FF0055).")

def apply_color_filter(img, tint, duotone, intensity, presets):
    """Applies monochrome tint, special B&W modes, or duotone grading while preserving alpha."""
    orig_rgba = img.convert("RGBA")
    r, g, b, alpha = orig_rgba.split()
    
    gray = ImageOps.grayscale(orig_rgba)
    
    if tint:
        tint_lower = tint.strip().lower()
        if tint_lower == 'grayscale':
            filtered_rgb = gray.convert("RGB")
        elif tint_lower == 'bitmap':
            filtered_rgb = gray.convert("1").convert("RGB")
        elif tint_lower == 'lineart':
            filtered_rgb = gray.point(lambda p: 255 if p > 128 else 0, mode='1').convert("RGB")
        elif tint_lower == 'sepia':
            filtered_rgb = ImageOps.colorize(gray, black=(30, 18, 8), white=(245, 225, 195))
        else:
            tr, tg, tb = parse_color_safe(tint, presets)
            dark_rgb = (int(tr * 0.12), int(tg * 0.12), int(tb * 0.12))
            filtered_rgb = ImageOps.colorize(gray, black=dark_rgb, white=(tr, tg, tb))
    else:
        shadow_color, highlight_color = duotone
        shadow_rgb = parse_color_safe(shadow_color, presets)
        highlight_rgb = parse_color_safe(highlight_color, presets)
        filtered_rgb = ImageOps.colorize(gray, black=shadow_rgb, white=highlight_rgb)
        
    if intensity < 100:
        orig_rgb = orig_rgba.convert("RGB")
        filtered_rgb = Image.blend(orig_rgb, filtered_rgb, intensity / 100.0)
        
    final_rgba = filtered_rgb.convert("RGBA")
    final_rgba.putalpha(alpha)
    return final_rgba

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input', required=False)
@click.option('-t', '--tint', default=None, help='Single color tint, preset name, hex, or special mode (grayscale, sepia, bitmap, lineart).')
@click.option('-d', '--duotone', nargs=2, default=None, help='Two colors for shadows and highlights (e.g., -d deepviolet neon).')
@click.option('-i', '--intensity', type=click.IntRange(1, 100), default=100, show_default=True, help='Filter blend intensity percentage (1-100).')
@click.option('--list-colors', is_flag=True, help='Display all available custom color presets from colors.json and exit.')
@click.option('--add-color', nargs=2, default=None, help='Save a new color preset to colors.json (e.g., --add-color lava "#FF3300").')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def filter_images(target_input, tint, duotone, intensity, list_colors, add_color, force):
    """Single & Bulk Color Filter (Tint & Duotone).
    
    Applies monochrome tinting, 1-bit B&W modes, or two-tone Cyberpunk duotone 
    color grading to a single image or an entire directory ('all'). Preserves alpha.
    
    Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, and GIF.
    """
    if add_color:
        name_arg, color_arg = add_color
        try:
            saved_name, saved_hex, existed = save_color_preset(name_arg, color_arg)
            action = "Updated" if existed else "Added"
            click.secho(f"Success! {action} preset '{saved_name}' -> {saved_hex} in colors.json.", fg='green', bold=True)
        except click.BadParameter as bp:
            click.secho(f"Error: {bp.format_message()}", fg='red', bold=True)
        except Exception as e:
            click.secho(f"Failed to save color preset: {e}", fg='red', bold=True)
        return

    presets = load_color_presets()

    if list_colors:
        click.secho("\n--- Available Color Presets (from colors.json) ---", fg='cyan', bold=True)
        for name, hex_val in presets.items():
            rgb = ImageColor.getrgb(hex_val)
            click.echo(f"  * {name:<14} -> {hex_val} (RGB{rgb})")
        click.echo("\nBuilt-in special modes: grayscale, sepia, bitmap, lineart")
        click.echo("You can also use any standard CSS color name (e.g., cyan, gold) or hex code (e.g., #FF0055).\n")
        return

    if not target_input:
        click.secho("Error: Missing argument 'TARGET_INPUT'. Provide a filename, 'all', --list-colors, or --add-color.", fg='red', bold=True)
        return
    if not tint and not duotone:
        click.secho("Error: You must specify either --tint (-t) or --duotone (-d).", fg='red', bold=True)
        return
    if tint and duotone:
        click.secho("Error: Please choose either --tint OR --duotone, not both at the same time.", fg='red', bold=True)
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = tuple()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            f for f in os.listdir(current_dir) 
            if f.lower().endswith(valid_extensions) 
            and not f.lower().endswith('_filtered.png')
            and not f.lower().endswith('_filtered.jpg')
            and not f.lower().endswith('_filtered.webp')
        )
        
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to filter.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to apply color filters to a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch filtering...")
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

    if tint:
        filter_desc = f"Tint ({tint})"
    else:
        c1, c2 = duotone
        filter_desc = f"Duotone ({c1} -> {c2})"

    click.echo(f"\n--- Starting Color Grading ({filter_desc} | Intensity: {intensity}%) ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, orig_ext = os.path.splitext(file_name)
        orig_ext_lower = orig_ext.lower()
        
        if orig_ext_lower in ('.jpg', '.jpeg'):
            out_ext = '.jpg'
            out_path = f"{file_name_without_ext}_filtered{out_ext}"
        elif orig_ext_lower == '.webp':
            out_ext = '.webp'
            out_path = f"{file_name_without_ext}_filtered{out_ext}"
        elif orig_ext_lower == '.png':
            out_ext = '.png'
            out_path = f"{file_name_without_ext}_filtered{out_ext}"
        else:
            out_ext = '.png'
            ext_tag = orig_ext_lower.lstrip('.')
            out_path = f"{file_name_without_ext}_{ext_tag}_filtered{out_ext}"
        
        try:
            click.echo(f"Filtering '{file_name}'...")
            with Image.open(file_name) as img:
                result_img = apply_color_filter(img, tint, duotone, intensity, presets)
                
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
                
        except click.BadParameter as bp:
            click.secho(f"Error: {bp.format_message()}", fg='red', bold=True)
            return
        except Exception as e:
            click.secho(f"  -> Failed to filter '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully filtered {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    filter_images()
