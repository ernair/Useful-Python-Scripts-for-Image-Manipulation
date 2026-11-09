# Useful Python Scripts for Image Manipulation

A collection of lightweight Python scripts designed to automate image background removal, transparent PNG exporting, aspect-ratio conversion, and high-quality Windows Icon (`.ico`) generation. 

These tools utilize a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving ugly pixelated edges.

## Features
- **Modern CLI Architecture:** Core scripts utilize the standard `click` library for robust argument parsing, automatic validation, and colorful terminal outputs.
- **Smart Color to Alpha:** Smoothly blends glowing borders and anti-aliased shadows instead of doing a harsh pixel cutoff.
- **True Multi-Resolution ICOs:** Embeds 6 scaling layers (from 16x16 up to 256x256 pixels) into a single `.ico` container so Windows desktop icons stay razor-sharp at any size.
- **Aspect-Ratio & Safety Protections:** Modern squaring scripts feature automated upscaling prevention to block blurry distortion.
- **Bulk & Single Processing:** Full support for both quick single asset preparation and full-folder batch processing.

## Prerequisites
The scripts require Python 3, **Pillow**, and the **Click** library. Install all dependencies via your terminal:
```bash
pip install Pillow click
```

---

## 🚀 Included Scripts (Modern Click Versions)

### 1. `batch_super_ico.py` (The Ultimate Bulk Tool)
Scans the current folder for all JPG, JPEG, and PNG files, applies smooth background removal, and outputs packed multi-resolution `.ico` files instantly. Features a built-in safety confirmation prompt for large batches.
```bash
python batch_super_ico.py <mode> [options]
# Modes: 1 = Black background, 2 = White background
# Flags: -f, --force = Bypass safety prompt, --png = Also export transparent PNGs

# Example:
python batch_super_ico.py 1 --png
```

### 2. `super_ico.py` (Single File Converter)
Automates the pipeline for a single target file. Validates file existence natively and exports a perfect multi-resolution `.ico` container using a clean command structure.
```bash
python super_ico.py <mode> <image_path>

# Example:
python super_ico.py 1 .\neon-lightning.png
```

---

## 🛠️ Image Resizing & Squaring Tools

### 3. `batch_crop_resize.py` (Center-Crop Square Resizer)
Forces a single image or an entire folder into a perfect square by scaling the shorter side and automatically cropping out any overflowing margins from the center. Features automated upscaling prevention to block blurry distortion. Supports both PNG and JPG exports.
```bash
python batch_crop_resize.py <size> <input> [-f] [--jpg]
# Input: Single filename (e.g. photo.jpg) OR '-a' for all images
```

### 4. `batch_pad_resize.py` (Padded Square Resizer)
Resizes images into a perfect square size without stretching, padding the empty margins with transparent, black, or white canvas space instead. Includes upscale prevention.
```bash
python batch_pad_resize.py <size> <input> [-f] [--black] [--white]
```

---

## 📁 Legacy Utils (Pure Python/sys.argv)

### 5. `batch_remove_bg.py` (Bulk PNG Exporting)
Scans the current folder for all images and applies pure background removal, exporting them strictly as transparent PNG files (`<name>_transparent.png`).
```bash
python batch_remove_bg.py <mode> [-f]
```

### 6. `remove_bg.py` (Single Background Cleaner)
Performs pure background removal on a single file and exports the result as a transparent PNG file.
```bash
python remove_bg.py <mode> <path_to_image>
```

### 7. `png_to_ico.py` (Single ICO Packer)
Converts an already transparent PNG image into a properly packed Windows `.ico` container with all standard resolution layers.
```bash
python png_to_ico.py <path_to_transparent_png>
```

## License
This project is open-source and free to use.
