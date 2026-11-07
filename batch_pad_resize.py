"""
Smart Padded Resizer (Single & Bulk Aspect-Ratio Preserver)
===========================================================
This command-line utility resizes images into a perfect square dimension without 
stretching or distorting the original content. It automatically scales the image 
to fit the target boundary and fills the empty margins with transparent, solid black, 
or solid white padding.

Safety Feature:
    Automatically detects and skips images where both dimensions are smaller than 
    the target size to prevent massive unnecessary padding margins.

Prerequisites:
    pip install Pillow

Usage:
    python batch_pad_resize.py <size> <input> [options]
"""

import os
import sys
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

def process_images(target_size, target_input, bg_mode, force_flag):
    """Handles both single image processing and batch processing based on input."""
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    files_to_process = []

    if target_input.lower() == '-a':
        files_to_process = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('_padded.png')]
        if not files_to_process:
            print("No matching JPG or PNG images found in this folder.")
            return
        print(f"Found {len(files_to_process)} images to batch process.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force_flag:
            print(f"\n[WARNING] You are about to resize a large batch of images ({len(files_to_process)} files).")
            response = input("Are you sure you want to proceed? (y/n): ").strip().lower()
            if response != 'y':
                print("Operation cancelled by user.")
                return
            print("Proceeding with batch conversion...")
        elif force_flag:
            print("Force flag (-f) detected. Bypassing safety prompts...")
    else:
        if not os.path.exists(target_input):
            print(f"Error: The file '{target_input}' was not found.")
            return
        if not target_input.lower().endswith(valid_extensions):
            print("Error: Unsupported file format. Please use JPG or PNG.")
            return
        files_to_process = [target_input]

    print(f"\n--- Starting Padded Resizing (Target: {target_size}x{target_size}, Padding: {bg_mode.upper()}) ---")
    success_count = 0
    skipped_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        output_path = f"{file_name_without_ext}_padded.png"
        
        try:
            with Image.open(file_name) as img:
                # Check if both dimensions are already smaller than target_size
                w, h = img.size
                if w < target_size and h < target_size:
                    print(f"-> Skipped '{file_name}': Image size ({w}x{h}) is fully smaller than target ({target_size}x{target_size}). Padding avoided.")
                    skipped_count += 1
                    continue

                print(f"Processing '{file_name}' ({w}x{h})...")
                final_img = pad_image_to_square(img, target_size, bg_mode)
                final_img.save(output_path, format="PNG")
                print(f"-> Saved successfully as: {output_path}")
                success_count += 1
        except Exception as e:
            print(f"-> Failed to process '{file_name}': {e}")

    print(f"\nFinished! Processed: {success_count} | Skipped (too small): {skipped_count} | Total files: {len(files_to_process)}")

def print_help_menu():
    """Prints a clear help menu to the console."""
    print("==========================================================================")
    print(" PNG/JPG Padded Resizer - Help Menu")
    print("==========================================================================")
    print("Resizes images into a perfect square size without stretching, adding")
    print("transparent, black, or white padding to the margins instead.\n")
    print("Note: This script automatically skips images whose dimensions are both")
    print("      smaller than the target size to avoid massive empty margins.\n")
    print("Usage:")
    print("  python batch_pad_resize.py <size> <input> [options]\n")
    print("Required Arguments:")
    print("  <size>    The target square pixel dimension (e.g., 1024 for 1024x1024).")
    print("  <input>   Specify a single filename (e.g., photo.jpg) OR use '-a' to")
    print("            process ALL images in the current folder.\n")
    print("Optional Flags:")
    print("  -f        Force mode. Bypasses the confirmation prompt for >5 files.")
    print("  --black   Fills the empty margins with solid black padding.")
    print("  --white   Fills the empty margins with solid white padding.")
    print("  -h, --help Show this help menu and exit.\n")
    print("Examples:")
    print("  python batch_pad_resize.py 1024 single_image.jpg")
    print("  python batch_pad_resize.py 1024 -a --white")
    print("==========================================================================")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if '-h' in args or '--help' in args or len(args) < 2:
        print_help_menu()
        sys.exit(0)
        
    force_active = '-f' in args
    black_active = '--black' in args
    white_active = '--white' in args
    
    if force_active:
        args.remove('-f')
    if black_active:
        args.remove('--black')
    if white_active:
        args.remove('--white')

    bg_selection = "transparent"
    if black_active:
        bg_selection = "black"
    elif white_active:
        bg_selection = "white"

    try:
        # FIXED: Extract items from the list using indexing safely
        input_size = int(args[0])
        input_target = args[1]
        process_images(input_size, input_target, bg_selection, force_active)
    except (ValueError, IndexError):
        print("Error: Invalid arguments. Use 'python batch_pad_resize.py --help' to see correct usage.")
