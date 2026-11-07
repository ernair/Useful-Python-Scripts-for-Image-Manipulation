# Useful Python Scripts for Image Manipulation

A collection of lightweight, dependency-free (except for `Pillow`) Python scripts designed to automate image background removal, 
transparent PNG exporting, aspect-ratio conversion, and high-quality Windows Icon (`.ico`) generation. 

These tools utilize a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or 
white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving ugly pixelated edges.

## Features
- **Smart Color to Alpha:** Smoothly blends glowing borders and anti-aliased shadows instead of doing a harsh pixel cutoff.
- **True Multi-Resolution ICOs:** Embeds 6 scaling layers (from 16x16 up to 256x256 pixels) into a single `.ico` container so Windows desktop icons stay razor-sharp at any size.
- **Two Resizing Methods:** Square your images perfectly either by adding padding (margins) or via clean center-cropping.
- **Upscaling Prevention:** Smart resolution detection skips small images automatically to preserve asset quality.
- **Bulk & Single Processing:** Tools available for both single asset preparation and full-folder batch conversions using flexible CLI flags.

## Prerequisites
The scripts require Python 3 and the **Pillow** library. Install it via your terminal:
```bash
pip install Pillow
```

## Included Scripts

### 1. `batch_crop_resize.py` (Center-Crop Square Resizer)
Forces a single image or an entire folder into a perfect square by scaling the shorter side and automatically cropping out any overflowing margins from the center. 
Features automated upscaling prevention to block blurry distortion. Supports both PNG and JPG exports.
```bash
python batch_crop_resize.py <size> <input> [-f] [--jpg]
# Input: Single filename (e.g. photo.jpg) OR '-a' for all images
```

### 2. `batch_pad_resize.py` (Padded Square Resizer)
Resizes images into a perfect square size without stretching, padding the empty margins with transparent, black, or white canvas space instead.
```bash
python batch_pad_resize.py <size> <input> [-f] [--black] [--white]
```

### 3. `batch_super_ico.py` (Bulk ICO Packing)
Scans the current folder for all JPG and PNG files, removes the background color smoothly, and outputs multi-resolution `.ico` files instantly. Features a volume-check safety prompt.
```bash
python batch_super_ico.py <mode> [-f] [--png]
```

### 4. `batch_remove_bg.py` (Bulk PNG Exporting)
Scans the current folder for all images and applies pure background removal, exporting them strictly as transparent PNG files (`<name>_transparent.png`).
```bash
python batch_remove_bg.py <mode> [-f]
```

### 5. `super_ico.py` (Single File Converter)
Automates the pipeline for a single file: opens an image, removes the background color smoothly, and outputs a multi-resolution `.ico` file.
```bash
python super_ico.py <mode> <path_to_image>
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
