"""
Batch PNG Background Remover (Bulk Color to Alpha Tool)
========================================================
This lightweight command-line utility automates the process of removing solid 
backgrounds from ALL images within the current working directory, exporting the 
results strictly as transparent PNG files.

It safely scans the folder for JPG, JPEG, and PNG files, implements a safety volume-check 
prompt to prevent accidental mass file creation, and applies a smooth GIMP-style 
'Color to Alpha' algorithm to cleanly preserve neon glows, soft shadows, and anti-aliasing.

Prerequisites:
    pip install Pillow

Usage:
    python batch_remove_bg.py <mode> [options]

Required Arguments:
    <mode>    The background color to turn transparent:
                1 = Bulk Process Black Backgrounds (Smooth Black to Alpha)
                2 = Bulk Process White Backgrounds (Smooth White to Alpha)

Optional Flags:
    -f        Force mode. Bypasses the confirmation prompt when a folder 
              contains more than 5 files.
    -h, --help Show the built-in help menu and usage examples.

Examples:
    python batch_remove_bg.py 1
    python batch_remove_bg.py 1 -f
    python batch_remove_bg.py --help
"""

import os
import sys
from PIL import Image

def remove_color_background(img, mode):
    """Applies a 'Color to Alpha' algorithm, making black or white
    backgrounds smoothly transparent and returning an RGBA PNG image.
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

def process_batch(mode, force_flag):
    """Loops through all JPG and PNG images in the current folder,
    removes backgrounds, and exports them as transparent PNG files.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    current_dir = os.getcwd()
    
    # Scan for images, ignoring already processed transparent files
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions) and not f.lower().endswith('_transparent.png')]
    
    if not files:
        print("No matching JPG or PNG images found in this folder.")
        return

    print(f"Found {len(files)} images to process in: {current_dir}")
    
    # Safety volume-check
    CRITICAL_LIMIT = 5
    if len(files) > CRITICAL_LIMIT and not force_flag:
        print(f"\n[WARNING] You are about to remove backgrounds from a large batch ({len(files)} files).")
        response = input("Are you sure you want to proceed? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation cancelled by user.")
            return
        print("Proceeding with batch transparency conversion...")
    elif force_flag:
        print("Force flag (-f) detected. Bypassing safety prompts...")

    print("\n--- Starting PNG Background Removal ---")
    success_count = 0

    for file_name in files:
        file_name_without_ext, _ = os.path.splitext(file_name)
        png_out_path = f"{file_name_without_ext}_transparent.png"
        
        try:
            print(f"Processing '{file_name}'...")
            with Image.open(file_name) as img:
                # Remove background and save purely as a transparent PNG
                transparent_img = remove_color_background(img, mode)
                transparent_img.save(png_out_path, format="PNG")
                print(f"-> Saved successfully as: {png_out_path}")
                success_count += 1
                
        except Exception as e:
            print(f"-> Failed to process '{file_name}': {e}")

    print(f"\nBatch processing finished! Successfully converted {success_count}/{len(files)} images to transparent PNG.")

def print_help_menu():
    """Prints a clear help menu to the console."""
    print("==========================================================================")
    print(" Batch PNG Background Remover - Help Menu")
    print("==========================================================================")
    print("This script processes all JPG, JPEG, and PNG images in the current folder.")
    print("It applies a smooth 'Color to Alpha' background removal and exports the")
    print("results strictly as transparent PNG files ('<name>_transparent.png').\n")
    print("Usage:")
    print("  python batch_remove_bg.py <mode> [options]\n")
    print("Required Arguments:")
    print("  <mode>    The background color to remove. Must be an integer:")
    print("              1 = Process Black Backgrounds (Smooth Black to Alpha)")
    print("              2 = Process White Backgrounds (Smooth White to Alpha)\n")
    print("Optional Flags:")
    print("  -f        Force mode. Bypasses the confirmation prompt when a folder")
    print("            contains more than 5 files.")
    print("  -h, --help Show this help menu and exit.\n")
    print("Examples:")
    print("  python batch_remove_bg.py 1")
    print("  python batch_remove_bg.py 1 -f")
    print("==========================================================================")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # Check for help flags
    if '-h' in args or '--help' in args or len(args) < 1:
        print_help_menu()
        sys.exit(0)
    
    # Check for force flag
    force_active = '-f' in args
    if force_active:
        args.remove('-f')

    try:
        # FIXED: Extract the first item from the list safely
        input_mode = int(args[0])
        if input_mode == 1 or input_mode == 2:
            if input_mode == 1:
                print("Mode: Bulk BLACK to Alpha PNG conversion selected.")
            else:
                print("Mode: Bulk WHITE to Alpha PNG conversion selected.")
            process_batch(input_mode, force_active)
        else:
            print("Error: Mode must be either 1 (Black) or 2 (White). Use --help for details.")
    except (ValueError, IndexError):
        print("Error: Invalid arguments. Use 'python batch_remove_bg.py --help' to see correct usage.")
