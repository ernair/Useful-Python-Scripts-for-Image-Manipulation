"""
Batch & Single EXIF Metadata Inspector & Stripper (via Click)
==============================================================
Inspects hidden EXIF/metadata tags inside raster images or strips all 
sensitive metadata (GPS coordinates, camera model, timestamps, software tags) 
while preserving image orientation and visual quality.

Supports all major raster formats: JPG, JPEG, PNG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_strip_exif.py <target_input> [options]

Examples:
    python batch_strip_exif.py photo.jpg --inspect
    python batch_strip_exif.py all --inspect
    python batch_strip_exif.py photo.jpg
    python batch_strip_exif.py all -f
"""

import os
import click
from PIL import Image, ImageOps, ExifTags

def extract_readable_metadata(img):
    """Extracts human-readable EXIF and info tags from an opened Pillow Image."""
    found_tags = {}
    
    # 1. Read standard EXIF data
    exif_data = img.getexif()
    if exif_data:
        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
            # Skip raw binary maker notes or massive byte dumps for clean display
            if isinstance(value, bytes):
                found_tags[tag_name] = f"<Binary data: {len(value)} bytes>"
            else:
                found_tags[tag_name] = str(value)
                
        # Check for nested GPSInfo IFD block
        gps_ifd = exif_data.get_ifd(0x8825)
        if gps_ifd:
            gps_details = {}
            for gps_id, gps_val in gps_ifd.items():
                gps_name = ExifTags.GPSTAGS.get(gps_id, f"GPS_{gps_id}")
                gps_details[gps_name] = str(gps_val)
            found_tags["GPSInfo (LOCATION DATA)"] = str(gps_details)

    # 2. Read PNG/WebP text chunks and other info headers (ignoring technical Pillow keys)
    technical_keys = {'jfif', 'jfif_version', 'jfif_unit', 'jfif_density', 'dpi', 'progression', 'icc_profile'}
    for k, v in img.info.items():
        if k.lower() not in technical_keys and k != 'exif':
            if isinstance(v, bytes):
                found_tags[f"Info:{k}"] = f"<Binary data: {len(v)} bytes>"
            else:
                found_tags[f"Info:{k}"] = str(v)
                
    return found_tags

def strip_image_metadata(img, out_path, out_ext):
    """Applies EXIF orientation physically, strips all metadata, and saves clean pixels."""
    # Bake orientation into actual pixels before stripping EXIF orientation tag
    oriented_img = ImageOps.exif_transpose(img)
    
    # Create a brand-new clean image from raw pixel data to guarantee zero leftover headers
    clean_img = Image.new(oriented_img.mode, oriented_img.size)
    clean_img.putdata(tuple(oriented_img.getdata()))
    
    if os.path.exists(out_path):
        os.remove(out_path)
        
    if out_ext == '.jpg':
        clean_img.convert("RGB").save(out_path, format="JPEG", quality=95)
    elif out_ext == '.webp':
        clean_img.save(out_path, format="WEBP", quality=92, method=6)
    elif out_ext == '.png':
        clean_img.save(out_path, format="PNG")
    elif out_ext == '.bmp':
        clean_img.convert("RGB").save(out_path, format="BMP")
    elif out_ext in ('.tiff', '.tif'):
        clean_img.save(out_path, format="TIFF")
    else:
        clean_img.save(out_path, format="PNG")

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('-i', '--inspect', is_flag=True, help='Inspect and display hidden EXIF/metadata tags without modifying files.')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
def process_exif(target_input, inspect, force):
    """Single & Bulk EXIF Metadata Inspector and Stripper.
    
    Inspects (--inspect) or permanently removes hidden EXIF, GPS location, 
    device info, and software tags from a single image or an entire folder ('all').
    
    Supports all major raster formats: JPG, JPEG, PNG, WebP, BMP, TIFF, and GIF.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = tuple()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            f for f in os.listdir(current_dir) 
            if f.lower().endswith(valid_extensions) 
            and '_clean.' not in f.lower()
        )
        
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to process.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force and not inspect:
            click.secho(f"\n[WARNING] You are about to strip metadata from a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch metadata removal...")
        elif force and not inspect:
            click.echo("Force flag (-f/--force) detected. Bypassing safety prompts...")
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        if not target_input.lower().endswith(valid_extensions):
            click.secho(f"Error: Unsupported file format. Supported: {', '.join(valid_extensions)}", fg='red', bold=True)
            return
        files_to_process = (target_input,)

    # --- MODE 1: INSPECT ONLY ---
    if inspect:
        click.secho("\n--- Inspecting Image Metadata ---", fg='cyan', bold=True)
        for file_name in files_to_process:
            try:
                with Image.open(file_name) as img:
                    tags = extract_readable_metadata(img)
                    click.secho(f"\nFile: {file_name}", fg='white', bold=True)
                    if not tags:
                        click.secho("  -> Clean! No EXIF or metadata tags found.", fg='green')
                    else:
                        for k, v in tags.items():
                            # Highlight GPS data in red as a privacy warning
                            color = 'red' if 'GPS' in k.upper() else 'yellow'
                            display_val = v if len(v) < 80 else f"{v[:77]}..."
                            click.secho(f"  * {k}: {display_val}", fg=color)
            except Exception as e:
                click.secho(f"  -> Could not read '{file_name}': {e}", fg='red')
        click.echo("")
        return

    # --- MODE 2: STRIP METADATA ---
    click.echo("\n--- Stripping EXIF & Metadata ---")
    success_count = 0

    for file_name in files_to_process:
        file_name_without_ext, orig_ext = os.path.splitext(file_name)
        orig_ext_lower = orig_ext.lower()
        
        if orig_ext_lower in ('.jpg', '.jpeg'):
            out_ext = '.jpg'
            out_path = f"{file_name_without_ext}_clean{out_ext}"
        elif orig_ext_lower in ('.webp', '.png', '.bmp', '.tiff', '.tif'):
            out_ext = '.tiff' if orig_ext_lower == '.tif' else orig_ext_lower
            out_path = f"{file_name_without_ext}_clean{out_ext}"
        else:
            # Convert GIF to clean PNG
            out_ext = '.png'
            ext_tag = orig_ext_lower.lstrip('.')
            out_path = f"{file_name_without_ext}_{ext_tag}_clean{out_ext}"
            
        try:
            click.echo(f"Cleaning '{file_name}'...")
            with Image.open(file_name) as img:
                strip_image_metadata(img, out_path, out_ext)
                click.secho(f"  -> Saved clean file: {out_path}", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to clean '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Successfully stripped metadata from {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)

if __name__ == "__main__":
    process_exif()
