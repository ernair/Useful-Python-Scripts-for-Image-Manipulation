"""
Smart Center-Crop Resizer (Single & Bulk Perfect Square Creator)
===============================================================
This utility forces any JPG or PNG image into a perfect square dimension without 
stretching. It scales the image to fully cover the target dimensions and automatically 
crops out the excess margins from the exact center (Center Crop).

Safety Feature: 
    Automatically detects and skips images that are smaller than the target size 
    to prevent low-quality upscaling blurry artifacts.

Prerequisites:
    pip install Pillow

Usage:
    python batch_crop_resize.py <size> <input> [options]

Required Arguments:
    <size>    The target square pixel dimension (e.g., 1024 for 1024x1024).
    <input>   Specify a single filename (e.g., photo.jpg) OR use '-a' to 
              process ALL images in the current folder.

Optional Flags:
    -f        Force mode. Bypasses the warning prompt when processing 
              more than 5 files in batch mode.
    --jpg     Saves the output as a high-quality JPG instead of PNG.
    -h, --help Show the built-in help menu and usage examples.

Examples:
    python batch_crop_resize.py 1024 single_image.jpg
    python batch_crop_resize.py 1024 -a
    python batch_crop_resize.py 1024 -a --jpg
"""

import os
import sys
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

def process_images(target_size, target_input, force_flag, save_jpg_flag):
    """Handles both single image cropping and batch cropping based on input."""
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    files_to_process = []

    out_ext = ".jpg" if save_jpg_flag else ".png"
    out_suffix = "_cropped"

    if target_input.lower() == '-a':
        files_to_process = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith(f'{out_suffix}.png') and not f.lower().endswith(f'{out_suffix}.jpg')]
        if not files_to_process:
            print("No matching JPG or PNG images found in this folder.")
            return
        print(f"Found {len(files_to_process)} images to batch process.")
        
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force_flag:
            print(f"\n[WARNING] You are about to CROP a large batch of images ({len(files_to_process)} files).")
            print("This will cut off edges from the sides or top/bottom to force a square shape.")
            response = input("Are you sure you want to proceed? (y/n): ").strip().lower()
            if response != 'y':
                print("Operation cancelled by user.")
                return
            print("Proceeding with batch cropping...")
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

    print(f"\n--- Starting Center-Cropped Resizing (Target: {target_size}x{target_size}, Format: {out_ext.upper()[1:]}) ---")
    success_count = 0
    skipped_count = 0

    for file_name in files_to_process:
        file_name_without_ext, _ = os.path.splitext(file_name)
        output_path = f"{file_name_without_ext}{out_suffix}{out_ext}"
        
        try:
            with Image.open(file_name) as img:
                # NEW UPGRADE: Check if image is smaller than the target size
                w, h = img.size
                if w < target_size or h < target_size:
                    print(f"-> Skipped '{file_name}': Image size ({w}x{h}) is smaller than target ({target_size}x{target_size}). Upscaling prevented.")
                    skipped_count += 1
                    continue

                print(f"Processing '{file_name}' ({w}x{h})...")
                final_img = crop_image_to_square(img, target_size, save_jpg_flag)
                
                if save_jpg_flag:
                    final_img.save(output_path, format="JPEG", quality=95)
                else:
                    final_img.save(output_path, format="PNG")
                    
                print(f"-> Saved successfully as: {output_path}")
                success_count += 1
        except Exception as e:
            print(f"-> Failed to process '{file_name}': {e}")

    print(f"\nFinished! Processed: {success_count} | Skipped (too small): {skipped_count} | Total files: {len(files_to_process)}")

def print_help_menu():
    """Prints a clear help menu to the diabetes console."""
    print("==========================================================================")
    print(" PNG/JPG Center-Crop Resizer - Help Menu")
    print("==========================================================================")
    print("Resizes images into a perfect square by scaling the shorter side and")
    print("automatically cropping out any overflowing edges from the exact center.\n")
    print("Note: This script automatically skips images that are smaller than the")
    print("      target size to prevent low-quality upscaling blurry artifacts.\n")
    print("Usage:")
    print("  python batch_crop_resize.py <size> <input> [options]\n")
    print("Required Arguments:")
    print("  <size>    The target square pixel dimension (e.g., 1024 for 1024x1024).")
    print("  <input>   Specify a single filename (e.g., photo.jpg) OR use '-a' to")
    print("            process ALL images in the current folder.\n")
    print("Optional Flags:")
    print("  -f        Force mode. Bypasses the confirmation prompt for >5 files.")
    print("  --jpg     Saves the output as a high-quality JPG instead of PNG.")
    print("  -h, --help Show this help menu and exit.\n")
    print("Examples:")
    print("  python batch_crop_resize.py 1024 single_image.jpg")
    print("  python batch_crop_resize.py 1024 -a --jpg")
    print("==========================================================================")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if '-h' in args or '--help' in args or len(args) < 2:
        print_help_menu()
        sys.exit(0)
        
    force_active = '-f' in args
    jpg_active = '--jpg' in args
    
    if force_active:
        args.remove('-f')
    if jpg_active:
        args.remove('--jpg')

    try:
        input_size = int(args[0])
        input_target = args[1]
        process_images(input_size, input_target, force_active, jpg_active)
    except (ValueError, IndexError):
        print("Error: Invalid arguments. Use 'python batch_crop_resize.py --help' to see correct usage.")
