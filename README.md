# Useful Python Scripts for Image Manipulation

A collection of lightweight, dependency-free (except for `Pillow`) Python scripts designed to automate image background removal and high-quality Windows Icon (`.ico`) generation. 

These tools utilize a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving ugly pixelated edges.

## Features
- **Smart Color to Alpha:** Smoothly blends glowing borders and anti-aliased shadows instead of doing a harsh pixel cutoff.
- **True Multi-Resolution ICOs:** Embeds 6 scaling layers (from 16x16 up to 256x256 pixels) into a single `.ico` container so Windows desktop icons stay razor-sharp at any size.
- **CLI-Ready:** Built to run directly from PowerShell, Git Bash, or CMD.

## Prerequisites
The scripts require Python 3 and the **Pillow** library. Install it via your terminal:
```bash
pip install Pillow
```

## Included Scripts

### 1. `super_ico.py` (The All-in-One Tool)
Automates the entire pipeline: opens an image, removes the solid background color smoothly, and outputs a multi-resolution `.ico` file instantly.
```bash
python super_ico.py <mode> <path_to_image>
# Modes: 1 = Black background, 2 = White background

# Example:
python super_ico.py 1 .\neon_lightning.png
```

### 2. `remove_bg.py` (Background Cleaner)
Performs pure background removal and exports the result as a transparent PNG file. Ideal for asset preparation.
```bash
python remove_bg.py <mode> <path_to_image>
# Modes: 1 = Remove Black, 2 = Remove White

# Example:
python remove_bg.py 1 .\matrix_folder.jpg
```

### 3. `png_to_ico.py` (ICO Packer)
Converts an already transparent PNG image into a properly packed Windows `.ico` container with all standard resolution layers.
```bash
python png_to_ico.py <path_to_transparent_png>

# Example:
python png_to_ico.py games_folder.png
```

## License
This project is open-source and free to use.
