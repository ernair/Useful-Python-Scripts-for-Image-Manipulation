"""
PNG to Multi-Resolution Windows ICO Converter
=============================================
A specialized utility script that converts already transparent PNG images into 
production-ready, crisp Windows Icon (.ico) files. 

Unlike basic online converters, this script generates a 'True Multi-Resolution' 
icon container by embedding 6 different scaling layers into a single file. This 
ensures your desktop icons remain perfectly sharp whether Windows displays them 
as small list icons or extra-large desktop assets.

Prerequisites:
    pip install Pillow

Usage:
    python png_to_ico.py <path_to_transparent_image.png>

Example:
    python png_to_ico.py games_folder.png

Output:
    Generates a scaled .ico file containing 16x16, 32x32, 48x48, 64x64, 128x128, 
    and 256x256 resolution layers in the same folder.
"""



import os
import sys
from PIL import Image


def convert_png_to_ico(png_path, ico_path=None):
    """Converts a transparent PNG image into a Windows-compatible .ico icon

    file.
    """
    # Check if the source PNG file actually exists
    if not os.path.exists(png_path):
        print(f"Error: The file '{png_path}' was not found.")
        return

    # If no output path is provided, use the same name but change extension to .ico
    if ico_path is None:
        ico_path = os.path.splitext(png_path)[0] + ".ico"

    try:
        # Open the PNG image using the Pillow library
        img = Image.open(png_path)

        # Define standard Windows desktop icon sizes
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

        # Save the file in ICO format, embedding all the defined sizes inside it
        img.save(ico_path, format="ICO", sizes=icon_sizes)
        print(f"Success! Icon saved as: {ico_path}")

    except Exception as e:
        print(f"Something went wrong during conversion: {e}")


if __name__ == "__main__":
    # Check if the user provided an image file name as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python png_to_ico.py <filename.png>")
        print("Example: python png_to_ico.py some_folder.png")
    else:
        # Get the filename from the command line argument
        input_file = sys.argv[1]
        convert_png_to_ico(input_file)
