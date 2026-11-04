"""
Smart Background Remover (Color to Alpha PNG Exporter)
=======================================================
This script performs a pure background removal on JPG or PNG images using a 
mathematical 'Color to Alpha' algorithm. It turns solid black or white backgrounds 
into soft, smooth transparency, making it perfect for preparing neon graphics, 
holograms, or logos without jagged pixelated edges.

Prerequisites:
    pip install Pillow

Usage:
    python remove_bg.py <mode> <path_to_image>
    
    Modes:
        1 = Remove Black Background smoothly
        2 = Remove White Background smoothly

Examples:
    python remove_bg.py 1 .\matrix_folder.jpg
    python remove_bg.py 2 .\light_icon.png

Output:
    Saves a clean, transparent alpha-channel image as '<original_name>_transparent.png' 
    in the same directory. The original file is left unmodified.
"""


import os
import sys
from PIL import Image


def remove_color_background(image_path, mode):
    """Opens a JPG/PNG image and applies a true 'Color to Alpha' algorithm,

    making black or white backgrounds smoothly transparent (antialiased).
    """
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' was not found.")
        return

    # FIXED: Properly unpack the filename tuple from splitext
    file_name_without_ext, _ = os.path.splitext(image_path)
    output_path = f"{file_name_without_ext}_transparent.png"

    try:
        with Image.open(image_path) as img:
            print(f"Processing '{image_path}'...")

            rgba_img = img.convert("RGBA")
            pixels = rgba_img.getdata()

            new_pixels = []
            
            if mode == 1:
                print("Mode 1 selected: Applying smooth BLACK to Alpha...")
                for item in pixels:
                    r, g, b, a = item
                    
                    # Calculate the brightness/luminance (max of channels defines the core color)
                    max_channel = max(r, g, b)
                    
                    if max_channel == 0:
                        new_pixels.append((0, 0, 0, 0))  # Pure black
                    else:
                        # Smooth transition: scale alpha and restore original vibrant color ratios
                        alpha = max_channel
                        new_r = int((r / max_channel) * 255)
                        new_g = int((g / max_channel) * 255)
                        new_b = int((b / max_channel) * 255)
                        new_pixels.append((new_r, new_g, new_b, alpha))
                        
            elif mode == 2:
                print("Mode 2 selected: Applying smooth WHITE to Alpha...")
                for item in pixels:
                    r, g, b, a = item
                    # Inverse for white background
                    min_channel = min(r, g, b)
                    
                    if min_channel == 255:
                        new_pixels.append((0, 0, 0, 0))  # Pure white
                    else:
                        alpha = 255 - min_channel
                        new_r = int(((r - min_channel) / (255 - min_channel)) * 255)
                        new_g = int(((g - min_channel) / (255 - min_channel)) * 255)
                        new_b = int(((b - min_channel) / (255 - min_channel)) * 255)
                        new_pixels.append((new_r, new_g, new_b, alpha))

            rgba_img.putdata(new_pixels)
            rgba_img.save(output_path, format="PNG")
            print(f"Success! Clean transparent image saved as: {output_path}")

    except Exception as e:
        print(f"Something went wrong during execution: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python remove_bg.py <mode> <filename>")
        print("Modes: 1 = Remove Black, 2 = Remove White")
        print("Example: python remove_bg.py 1 some_folder.jpg")
    else:
        try:
            input_mode = int(sys.argv[1])
            input_file = sys.argv[2]

            if input_mode == 1 or input_mode == 2:
                remove_color_background(input_file, input_mode)
            else:
                print("Error: Mode must be either 1 (Black) or 2 (White).")
                
        except ValueError:
            print("Error: The first argument (mode) must be an integer (1 or 2).")
