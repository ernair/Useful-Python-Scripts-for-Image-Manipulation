"""
Smart Padded Resizer (Single & Bulk Aspect-Ratio Preserver via Click)
===================================================================
This command-line utility resizes images into a perfect square dimension without 
stretching or distorting the original content. It automatically scales the image 
to fit the target boundary and fills the empty margins with transparent, solid black, 
or solid white padding.

Safety Feature:
    Automatically detects and skips images where both dimensions are smaller than 
    the target size to prevent massive unnecessary padding margins.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_pad_resize.py <size> <target_input> [options]
"""

import os
import sys
import click
from PIL import Image

def pad_image_to_square(img, target_size, bg_mode):
    """Resizes an image maintaining its aspect ratio, then centers it
    on a square canvas with either transparent, black, or white padding.
    """
    # thumbnail() naturally prevents upscaling, maintaining original size if smaller
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
    
    if bg_mode == "black":
        background = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 255))
    elif bg_mode == "white":
        background = Image.new("RGBA", (target_size, target_size), (255, 255, 255, 255))
    else:
        background = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
        
    offset = ((target_size - img.width) // 2, (target_size - img.height) // 2)
    background.paste(img.convert("RGBA"), offset, img.convert("RGBA"))
    return background

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('size', type=int)
@click.argument('target_input')
@click.option('-f', '--force', is_flag=True, help='Bypass the confirmation prompt for large batches (more than 5 files).')
@click.option('--black', is_flag=True, help='Fill the empty margins with solid black padding.')
@click.option('--white', is_flag=True, help='Fill the empty margins with solid white padding.')
def process_images(size, target_input, force, black, white):
    """Smart Padded Resizer.
    
    Resizes images into a perfect square size without stretching, padding 
    the empty margins with transparent, black, or white canvas space instead.
    
    TARGET_INPUT can be a specific filename (e.g., photo.jpg) OR use 'all' 
    to process ALL images in the current folder.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    files_to_process = []

    # Check for 'all' instead of '-a' to prevent CLI parameter confusion
    if target_input.lower() == 'all':
        files_to_process = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('_padded.png')]
        if not files_to_process:
            click.secho("No matching JPG or PNG images found in this folder.", fg='yellow')
            return
        click.echo(f"Found {len(files_to_process)} images to batch process.")
        
        # Safety check for batch mode using Click's built-in confirmation
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to resize a large batch of images ({len(files_to_process)} files).", fg='yellow', bold=True)
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
            click.secho("Error: Unsupported file format. Please use JPG or PNG.", fg='red', bold=True)
            return
        files_to_process = [target_input]

    # Determine background mode
    bg_selection = "transparent"
    if black:
        bg_selection = "black"
    elif white:
        bg_selection = "white"

    click.echo(f"\n--- Starting Padded Resizing (Target: {size}x{size}, Padding: {bg_selection.upper()}) ---")
    success_count = 0
    skipped_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        output_path = f"{file_name_without_ext}_padded.png"
        
        try:
            with Image.open(file_name) as img:
                w, h = img.size
                if w < size and h < size:
                    click.secho(f"  -> Skipped '{file_name}': Size ({w}x{h}) is fully smaller than target ({size}x{size}). Padding avoided.", fg='yellow')
                    skipped_count += 1
                    continue

                print(f"Processing '{file_name}' ({w}x{h})...")
                final_img = pad_image_to_square(img, size, bg_selection)
                final_img.save(output_path, format="PNG")
                click.secho(f"  -> Saved successfully as: {output_path}", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Processed: {success_count} | Skipped: {skipped_count} | Total files: {len(files_to_process)}", fg='green', bold=True)

if __name__ == "__main__":
    process_images()
