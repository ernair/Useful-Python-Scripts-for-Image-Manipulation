"""
Smart Center-Crop Resizer (Single & Bulk Perfect Square Creator via Click)
========================================================================
This utility forces any JPG or PNG image into a perfect square dimension without 
stretching. It scales the image to fully cover the target dimensions and automatically 
crops out the excess margins from the exact center (Center Crop).

Safety Feature: 
    Automatically detects and skips images that are smaller than the target size 
    to prevent low-quality upscaling blurry artifacts.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_crop_resize.py <size> <target_input> [options]
"""

import os
import sys
import click
from PIL import Image

def crop_image_to_square(img, target_size, save_jpg=False):
    """Resizes an image maintaining its aspect ratio to cover the target size,
    then crops out a perfect square from the exact center.
    """
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height
    
    if aspect_ratio > 1:
        new_height = target_size
        new_width = int(target_size * aspect_ratio)
    else:
        new_width = target_size
        new_height = int(target_size / aspect_ratio)
        
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    left = (new_width - target_size) // 2
    top = (new_height - target_size) // 2
    right = left + target_size
    bottom = top + target_size
    
    cropped_img = resized_img.crop((left, top, right, bottom))
    
    if save_jpg:
        if cropped_img.mode in ("RGBA", "LA") or (cropped_img.mode == "P" and "transparency" in cropped_img.info):
            background = Image.new("RGB", (target_size, target_size), (255, 255, 255))
            background.paste(cropped_img, (0, 0), cropped_img.convert("RGBA"))
            return background
        return cropped_img.convert("RGB")
        
    return cropped_img

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('size', type=int)
@click.argument('target_input')
@click.option('-f', '--force', is_flag=True, help='Bypass the safety confirmation prompt for large batches (more than 5 files).')
@click.option('--jpg', is_flag=True, help='Save the output as a high-quality JPG instead of PNG (transparency turns white).')
def process_images(size, target_input, force, jpg):
    """Smart Center-Crop Resizer.
    
    Resizes images into a perfect square by scaling the shorter side and 
    automatically cropping out overflowing edges from the center.
    
    TARGET_INPUT can be a specific filename (e.g., photo.jpg) OR use 'all' 
    to process ALL images in the current folder.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    files_to_process = []  # FIXED: Empty list initialization here safely

    out_ext = ".jpg" if jpg else ".png"
    out_suffix = "_cropped"

    # Check for 'all' instead of '-a' to prevent CLI parameter confusion
    if target_input.lower() == 'all':
        files_to_process = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith(f'{out_suffix}.png') and not f.lower().endswith(f'{out_suffix}.jpg')]
        if not files_to_process:
            click.secho("No matching JPG or PNG images found in this folder.", fg='yellow')
            return
        click.echo(f"Found {len(files_to_process)} images to batch process.")
        
        # Safety check for batch mode using Click's built-in confirmation
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to CROP a large batch of images ({len(files_to_process)} files).", fg='yellow', bold=True)
            click.echo("This will cut off edges from the sides or top/bottom to force a square shape.")
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch cropping...")
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

    click.echo(f"\n--- Starting Center-Cropped Resizing (Target: {size}x{size}, Format: {out_ext.upper()[1:]}) ---")
    success_count = 0
    skipped_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        output_path = f"{file_name_without_ext}{out_suffix}{out_ext}"
        
        try:
            with Image.open(file_name) as img:
                w, h = img.size
                if w < size or h < size:
                    click.secho(f"  -> Skipped '{file_name}': Size ({w}x{h}) is smaller than target ({size}x{size}). Upscaling prevented.", fg='yellow')
                    skipped_count += 1
                    continue

                click.echo(f"Processing '{file_name}' ({w}x{h})...")
                final_img = crop_image_to_square(img, size, jpg)
                
                if jpg:
                    final_img.save(output_path, format="JPEG", quality=95)
                else:
                    final_img.save(output_path, format="PNG")
                    
                click.secho(f"  -> Saved successfully as: {output_path}", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Processed: {success_count} | Skipped: {skipped_count} | Total files: {len(files_to_process)}", fg='green', bold=True)

if __name__ == "__main__":
    process_images()
