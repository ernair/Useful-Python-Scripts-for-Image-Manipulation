"""
Super ICO Converter (Color to Alpha + Windows ICO Generator)
============================================================
This script automates the entire process of creating high-quality, 
multi-resolution Windows desktop icons (.ico) from any source image (JPG/PNG).

It applies a smart mathematical 'Color to Alpha' algorithm (similar to GIMP/Photoshop) 
to smoothly remove solid black or white backgrounds, preserving glowing neon edges 
and soft semi-transparent anti-aliased shadows.

Prerequisites:
    pip install Pillow

Usage:
    python super_ico.py <mode> <path_to_image>
    
    Modes:
        1 = Process Black Background (Smooth Black to Alpha)
        2 = Process White Background (Smooth White to Alpha)

Examples:
    python super_ico.py 1 .\neon_lightning.png
    python super_ico.py 2 .\company_logo.jpg

Output:
    Creates a true 'Multi-Resolution' .ico file in the same directory containing 
    all standard Windows desktop layers (16x16 up to 256x256 pixels) for crisp scaling.
    The original source file remains completely untouched.
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
        print("-> Applying smooth BLACK to Alpha...")
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
        print("-> Applying smooth WHITE to Alpha...")
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


def create_ultimate_ico(image_path, mode):
    """Processes the image and saves it directly as a multi-resolution Windows

    .ico file.
    """
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' was not found.")
        return

    # Generate the final .ico file path
    file_name_without_ext, _ = os.path.splitext(image_path)
    ico_path = f"{file_name_without_ext}.ico"

    try:
        # 1. Open the original image
        with Image.open(image_path) as img:
            print(f"Processing '{image_path}'...")

            # 2. Run the smart transparency background removal
            transparent_img = remove_color_background(img, mode)

            # 3. Define standard Windows desktop icon sizes
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

            # 4. Save directly as ICO containing all layers
            transparent_img.save(ico_path, format="ICO", sizes=icon_sizes)
            print(f"Success! Ultimate multi-resolution icon saved as: {ico_path}")

    except Exception as e:
        print(f"Something went wrong during execution: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python super_ico.py <mode> <filename>")
        print("Modes: 1 = Process Black Background, 2 = Process White Background")
        print("Example: python super_ico.py 1 neon_lightning.png")
    else:
        try:
            input_mode = int(sys.argv[1])
            input_file = sys.argv[2]

            if input_mode == 1 or input_mode == 2:
                create_ultimate_ico(input_file, input_mode)
            else:
                print("Error: Mode must be either 1 (Black) or 2 (White).")
                
        except ValueError:
            print("Error: The first argument (mode) must be an integer (1 or 2).")
