"""
Batch Super ICO & PNG Converter (Bulk Color to Alpha Tool)
==========================================================
This production-ready command-line tool automates background removal, transparent 
PNG exporting, and Windows Icon (.ico) generation for ALL images within the current 
working directory.

It scans the folder for JPG, JPEG, and PNG files, implements a safety volume-check 
prompt to prevent accidental mass file creation, and applies a smooth GIMP-style 
'Color to Alpha' algorithm to cleanly preserve neon glows, soft shadows, and anti-aliasing.

Prerequisites:
    pip install Pillow

Usage:
    python batch_super_ico.py <mode> [options]

Required Arguments:
    <mode>    The background color to turn transparent:
                1 = Process Black Backgrounds (Smooth Black to Alpha)
                2 = Process White Backgrounds (Smooth White to Alpha)

Optional Flags:
    -f        Force mode. Bypasses the confirmation prompt when a folder 
              contains a large batch of images (more than 5 files).
    --png     PNG Export. Additionally saves the transparent results as 
              individual PNG files ('<name>_transparent.png').
    -h, --help Show the built-in help menu and usage examples.

Examples:
    python batch_super_ico.py 1
    python batch_super_ico.py 1 --png
    python batch_super_ico.py 1 -f --png
    python batch_super_ico.py --help
"""

import os
import sys
from PIL import Image

def remove_color_background(img, mode):
    """Applies a 'Color to Alpha' algorithm, making black or white
    backgrounds smoothly transparent.
    """
    rgba_img = img.convert("RGBA")
    pixels = rgba_img.getdata()
    new_pixels = []
    
    if mode == 1:
        for item in pixels:
            r, g, b, a = item
            max_channel = max(r, g, b)
            if max_channel == 0:
                new_pixels.append((0, 0, 0, 0))
            else:
                alpha = max_channel
                new_r = int((r / max_channel) * 255)
                new_g = int((g / max_channel) * 255)
                new_b = int((b / max_channel) * 255)
                new_pixels.append((new_r, new_g, new_b, alpha))
                
    elif mode == 2:
        for item in pixels:
            r, g, b, a = item
            min_channel = min(r, g, b)
            if min_channel == 255:
                new_pixels.append((0, 0, 0, 0))
            else:
                alpha = 255 - min_channel
                new_r = int(((r - min_channel) / (255 - min_channel)) * 255)
                new_g = int(((g - min_channel) / (255 - min_channel)) * 255)
                new_b = int(((b - min_channel) / (255 - min_channel)) * 255)
                new_pixels.append((new_r, new_g, new_b, alpha))

    rgba_img.putdata(new_pixels)
    return rgba_img

def process_batch(mode, force_flag, save_png_flag):
    """Loops through all JPG and PNG images in the current folder,
    removes backgrounds, and saves them as Windows .ico files and optionally transparent PNGs.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    
    # Analyze and count files (ignore existing .ico files and previously generated _transparent.png files)
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('.ico') and not f.lower().endswith('_transparent.png')]
    
    if not files:
        print("No matching JPG or PNG images found in this folder.")
        return

    print(f"Found {len(files)} images to process in: {current_dir}")
    
    # Safety check
    CRITICAL_LIMIT = 5
    if len(files) > CRITICAL_LIMIT and not force_flag:
        print(f"\n[WARNING] You are about to process a large batch of images ({len(files)} files).")
        response = input("Are you sure you want to proceed? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation cancelled by user.")
            return
        print("Proceeding with batch conversion...")
    elif force_flag:
        print("Force flag (-f) detected. Bypassing safety prompts...")

    print("\n--- Starting Conversion ---")
    success_count = 0

    for file_name in files:
        file_name_without_ext, _ = os.path.splitext(file_name)
        ico_path = f"{file_name_without_ext}.ico"
        png_out_path = f"{file_name_without_ext}_transparent.png"
        
        try:
            print(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                # 1. Remove background
                transparent_img = remove_color_background(img, mode)
                
                # 2. Save ICO (always done)
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                transparent_img.save(ico_path, format="ICO", sizes=icon_sizes)
                print(f"-> Saved successfully as: {ico_path}")
                
                # 3. Save PNG (only if --png flag is active)
                if save_png_flag:
                    transparent_img.save(png_out_path, format="PNG")
                    print(f"-> Saved successfully as: {png_out_path}")
                    
                success_count += 1
                
        except Exception as e:
            print(f"-> Failed to process '{file_name}': {e}")

    print(f"\nBatch processing finished! Successfully converted {success_count}/{len(files)} images.")

def print_help_menu():
    """Prints a beautiful and clear help menu to the console."""
    print("==========================================================================")
    print(" Batch Super ICO Converter - Help Menu")
    print("==========================================================================")
    print("This script processes all JPG, JPEG, and PNG images in the current folder.")
    print("It applies a smooth 'Color to Alpha' background removal and packs them")
    print("directly into multi-resolution Windows Icon (.ico) containers.\n")
    print("Usage:")
    print("  python batch_super_ico.py <mode> [options]\n")
    print("Required Arguments:")
    print("  <mode>    The background color to remove. Must be an integer:")
    print("              1 = Process Black Backgrounds (Smooth Black to Alpha)")
    print("              2 = Process White Backgrounds (Smooth White to Alpha)\n")
    print("Optional Flags:")
    print("  -f        Force mode. Bypasses the confirmation prompt when a folder")
    print("            contains a large batch of images (more than 5 files).")
    print("  --png     PNG Export. Additionally saves the transparent results as")
    print("            individual PNG files ('<name>_transparent.png').")
    print("  -h, --help Show this help menu and exit.\n")
    print("Examples:")
    print("  python batch_super_ico.py 1")
    print("  python batch_super_ico.py 1 --png")
    print("  python batch_super_ico.py 1 -f --png")
    print("==========================================================================")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # Check for help flags first
    if '-h' in args or '--help' in args or len(args) < 1:
        print_help_menu()
        sys.exit(0)
    
    # Check for other optional flags
    force_active = '-f' in args
    png_active = '--png' in args
    
    # Clean flags out of the args list to isolate the mode integer
    if force_active:
        args.remove('-f')
    if png_active:
        args.remove('--png')

    try:
        input_mode = int(args[0])
        if input_mode == 1 or input_mode == 2:
            if input_mode == 1:
                print("Mode: BLACK to Alpha conversion selected.")
            else:
                print("Mode: WHITE to Alpha conversion selected.")
            process_batch(input_mode, force_active, png_active)
        else:
            print("Error: Mode must be either 1 (Black) or 2 (White). Use --help for usage details.")
    except (ValueError, IndexError):
        print("Error: Invalid arguments. Use 'python batch_super_ico.py --help' to see correct usage.")
