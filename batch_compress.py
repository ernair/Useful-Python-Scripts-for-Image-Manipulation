"""
Batch WebP Image Compressor (Single & Bulk Optimizer via Click)
===============================================================
This utility converts and compresses JPG, JPEG, and PNG images into the modern, 
lightweight WebP format while preserving transparency (Alpha channels) and high visual quality.

It utilizes the 'click' library for clean argument parsing, adjustable compression quality, 
automated validation, and real-time storage savings calculation.

Prerequisites:
    pip install Pillow click

Usage:
    python batch_compress.py <target_input> [options]

Required Arguments:
    <target_input>  Specify a single filename (e.g., photo.png) OR use 'all' 
                    to compress ALL images in the current folder.

Optional Flags:
    -q, --quality   Compression quality from 1 to 100 (default: 80).
    -f, --force     Force mode. Bypasses the confirmation prompt for >5 files.
    -h, --help      Show the built-in help menu and usage examples.

Examples:
    python batch_compress.py single_image.png
    python batch_compress.py all
    python batch_compress.py all -q 90
    python batch_compress.py all -q 75 -f
"""

import os
import click
from PIL import Image

def format_bytes(size):
    """Converts bytes to a human-readable KB or MB string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('-q', '--quality', type=click.IntRange(1, 100), default=80, show_default=True, help='WebP compression quality (1-100).')
@click.option('-f', '--force', is_flag=True, help='Bypass the safety confirmation prompt for large batches (more than 5 files).')
def compress_images(target_input, quality, force):
    """Modern WebP Image Compressor.
    
    Compresses JPG and PNG files into lightweight WebP format while preserving 
    transparency and visual fidelity. Calculates total disk space saved.
    
    TARGET_INPUT can be a specific filename (e.g., banner.png) OR use 'all' 
    to compress ALL images in the current folder.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    files_to_process = []

    # Identify target files
    if target_input.lower() == 'all':
        files_to_process = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions)]
        if not files_to_process:
            click.secho("No matching JPG or PNG images found in this folder.", fg='yellow')
            return
        click.echo(f"Found {len(files_to_process)} images to compress.")
        
        # Safety check for batch mode
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to compress a large batch of images ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch compression...")
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

    click.echo(f"\n--- Starting WebP Compression (Quality: {quality}/100) ---")
    success_count = 0
    total_original_bytes = 0
    total_new_bytes = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        output_path = f"{file_name_without_ext}.webp"
        
        try:
            original_size = os.path.getsize(file_name)
            click.echo(f"Compressing '{file_name}' ({format_bytes(original_size)})...")
            
            with Image.open(file_name) as img:
                # Save as WebP (method=6 ensures best compression ratio)
                img.save(output_path, format="WEBP", quality=quality, method=6)
                
            new_size = os.path.getsize(output_path)
            total_original_bytes += original_size
            total_new_bytes += new_size
            
            # Calculate percentage saved for this file
            saved_pct = ((original_size - new_size) / original_size) * 100 if original_size > 0 else 0
            
            click.secho(f"  -> Saved as '{output_path}' ({format_bytes(new_size)} | Saved {saved_pct:.1f}%)", fg='cyan')
            success_count += 1
            
        except Exception as e:
            click.secho(f"  -> Failed to compress '{file_name}': {e}", fg='red', bold=True)

    # Summary with total savings
    if success_count > 0:
        total_saved = total_original_bytes - total_new_bytes
        total_pct = (total_saved / total_original_bytes) * 100 if total_original_bytes > 0 else 0
        click.secho(f"\nFinished! Compressed {success_count}/{len(files_to_process)} image(s).", fg='green', bold=True)
        click.secho(f"Total Space Saved: {format_bytes(total_saved)} ({total_pct:.1f}% reduction)", fg='green', bold=True)

if __name__ == "__main__":
    compress_images()
