# Useful Python Scripts for Image Manipulation

A collection of lightweight, dependency-free (except for `Pillow`) Python scripts designed to automate image background removal and high-quality Windows Icon (`.ico`) generation. 

These tools utilize a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving ugly pixelated edges.

## Features
- **Smart Color to Alpha:** Smoothly blends glowing borders and anti-aliased shadows instead of doing a harsh pixel cutoff.
- **True Multi-Resolution ICOs:** Embeds 6 scaling layers (from 16x16 up to 256x256 pixels) into a single `.ico` container so Windows desktop icons stay razor-sharp at any size.
- **Bulk Processing:** Includes a batch processor to clean and convert an entire folder of images in one command.
- **CLI-Ready:** Built to run directly from PowerShell, Git Bash, or CMD with built-in `--help` menus.

## Prerequisites
The scripts require Python 3 and the **Pillow** library. Install it via your terminal:
```bash
pip install Pillow
```

## Included Scripts

### 1. `batch_super_ico.py` (The Ultimate Bulk Tool)
Scans the current folder for all JPG and PNG files, processes them automatically, and features a built-in safety check for large batches.
```bash
python batch_super_ico.py <mode> [-f] [--png]
# Modes: 1 = Black background, 2 = White background
# Flags: -f = Bypass safety prompt, --png = Also export transparent PNG

# Example (Process all black backgrounds and export both ICO and PNG):
python batch_super_ico.py 1 --png
```

### 2. `super_ico.py` (Single File Converter)
Automates the pipeline for a single file: opens an image, removes the background color smoothly, and outputs a multi-resolution `.ico` file instantly.
```bash
python super_ico.py <mode> <path_to_image>

# Example:
python super_ico.py 1 .\neon_lightning.png
```

### 3. `remove_bg.py` (Background Cleaner)
Performs pure background removal on a single file and exports the result as a transparent PNG file.
```bash
python remove_bg.py <mode> <path_to_image>

# Example:
python remove_bg.py 1 .\matrix_folder.jpg
```

### 4. `png_to_ico.py` (ICO Packer)
Converts an already transparent PNG image into a properly packed Windows `.ico` container with all standard resolution layers.
```bash
python png_to_ico.py <path_to_transparent_png>
```

## License
This project is open-source and free to use.
