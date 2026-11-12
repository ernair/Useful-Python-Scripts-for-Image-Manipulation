# Useful Python Scripts for Image Manipulation

A collection of modern, lightweight Python command-line tools designed to automate image background removal, transparent PNG exporting, aspect-ratio conversion, WebP optimization, image compositing, and high-quality Windows Icon (`.ico`) generation. 

All scripts utilize the **Click** library for clean CLI argument parsing, automated input validation, and colorful terminal outputs. Background removal tools rely on a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving jagged edges.

## Features
- **Modern CLI Architecture:** Built 100% on the `click` library for robust argument parsing, built-in `--help` menus, and native terminal coloring.
- **Two-Way Image Compositing:** Center foreground icons onto base backgrounds (or stamp one logo onto an entire folder of backgrounds) with proportional scaling and multi-format export.
- **Smart Color to Alpha:** Smoothly blends glowing borders and anti-aliased shadows instead of doing a harsh pixel cutoff.
- **True Multi-Resolution ICOs:** Embeds 6 scaling layers (from 16x16 up to 256x256 pixels) into a single `.ico` container so Windows desktop icons stay razor-sharp at any size.
- **Next-Gen WebP Compression:** Converts heavy PNG/JPG assets into lightweight `.webp` files with real-time storage savings calculation.
- **Aspect-Ratio & Safety Protections:** Squaring scripts feature automated upscaling prevention to block blurry distortion, alongside batch volume confirmation prompts.

## Prerequisites
The scripts require Python 3, **Pillow**, and the **Click** library. Install all dependencies via your terminal:
```bash
pip install Pillow click
```

---

## 🚀 Included Scripts

### 1. `batch_overlay.py` (Two-Way Image Overlay Compositor)
Places a foreground image dead-center onto a base background image. Supports `all` in either position (`all base.png` or `logo.png all`), proportional downscaling, relative size locking to the base image, and multiple raster export formats (`png`, `jpg`, `webp`).
```bash
python batch_overlay.py <foreground_input> <base_input> [-s SCALE] [-l] [--format FORMAT] [-f]
# Flags: -s/--scale (0-99% shrink), -l/--lock (scale relative to base), --format (png/jpg/webp)

# Example (Stamp one logo onto all backgrounds, locked to base and shrunk 50%):
python batch_overlay.py logo.png all -l -s 50
```

### 2. `batch_compress.py` (Single & Bulk WebP Optimizer)
Converts and compresses JPG, JPEG, and PNG images into the modern, lightweight `.webp` format while preserving transparency and resolution. Calculates total disk space saved in real time.
```bash
python batch_compress.py <target_input> [-q QUALITY] [-f]
# Input: Single filename (e.g., banner.png) OR 'all' for the entire folder
# Flags: -q/--quality (1-100, default: 80), -f/--force (bypass batch prompt)

# Example:
python batch_compress.py all -q 85
```

### 3. `batch_super_ico.py` (Bulk ICO Generator)
Scans the current folder for all JPG, JPEG, and PNG files, applies smooth background removal, and outputs packed multi-resolution `.ico` files instantly. Features a built-in safety confirmation prompt for large batches.
```bash
python batch_super_ico.py <mode> [-f] [--png]
# Modes: 1 = Black background, 2 = White background
# Flags: -f/--force = Bypass safety prompt, --png = Also export transparent PNGs

# Example:
python batch_super_ico.py 1 --png
```

### 4. `super_ico.py` (Single File ICO Converter)
Automates the pipeline for a single target file. Validates file existence natively and exports a perfect multi-resolution `.ico` container.
```bash
python super_ico.py <mode> <image_path>

# Example:
python super_ico.py 1 .\neon-lightning.png
```

### 5. `batch_crop_resize.py` (Center-Crop Square Resizer)
Forces a single image or an entire folder (`all`) into a perfect square by scaling the shorter side and automatically cropping out any overflowing margins from the center. Features automated upscaling prevention and optional JPG export.
```bash
python batch_crop_resize.py <size> <target_input> [-f] [--jpg]

# Example:
python batch_crop_resize.py 1024 all --jpg
```

### 6. `batch_pad_resize.py` (Padded Square Resizer)
Resizes a single image or an entire folder (`all`) into a perfect square size without stretching, padding the empty margins with transparent, black, or white canvas space instead. Includes upscale prevention.
```bash
python batch_pad_resize.py <size> <target_input> [-f] [--black] [--white]

# Example:
python batch_pad_resize.py 1024 all --white
```

### 7. `batch_remove_bg.py` (Bulk PNG Background Remover)
Scans the current folder for all images and applies pure background removal, exporting them strictly as transparent PNG files (`<name>_transparent.png`).
```bash
python batch_remove_bg.py <mode> [-f]
```

### 8. `remove_bg.py` (Single Background Cleaner)
Performs pure background removal on a single file and exports the result as a transparent PNG file.
```bash
python remove_bg.py <mode> <image_path>
```

### 9. `png_to_ico.py` (Single ICO Packer)
Converts an already transparent PNG image into a properly packed Windows `.ico` container with all standard resolution layers.
```bash
python png_to_ico.py <path_to_transparent_png>
```

## License
This project is open-source and free to use.
