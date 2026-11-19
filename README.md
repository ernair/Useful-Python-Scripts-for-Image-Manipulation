# Useful Python Scripts for Image Manipulation

A collection of 10 modern, lightweight Python command-line tools designed to automate image background removal, transparent PNG/WebP exporting, raster format conversion, aspect-ratio squaring, WebP optimization, image compositing, watermarking, color grading, EXIF metadata stripping, and high-quality Windows Icon (`.ico`) generation. 

All scripts utilize the **Click** library for clean CLI argument parsing, automated input validation, and colorful terminal outputs. Background removal tools rely on a smart mathematical **Color to Alpha** algorithm (similar to GIMP and Photoshop) to smoothly convert solid black or white backgrounds into alpha transparency—perfect for neon graphics, sci-fi desktop themes, and logos without leaving jagged edges.

## Features
- **Modern CLI Architecture:** Built 100% on the `click` library for robust argument parsing, built-in `--help` menus, and native terminal coloring.
- **Privacy & EXIF Metadata Control:** Inspect hidden EXIF, GPS location, and software tags (`--inspect`) or strip all metadata cleanly while preserving physical image orientation.
- **Creative Color Grading & 1-Bit Modes:** Apply single-color tints, built-in special modes (`grayscale`, `sepia`, 1-bit dithered `bitmap`, and sharp `lineart`), and two-tone Cyberpunk duotones using an editable `colors.json` preset bank with CLI color saving (`--add-color`).
- **Customizable Image Watermarking:** Stamp proportional text (with custom colors and auto-shadows) or transparent logos onto single images or entire directories with margin and opacity controls.
- **Universal Raster Format Converter:** Convert single images or whole directories between `PNG`, `JPG`, `WebP`, `BMP`, `TIFF`, and `GIF` with automatic transparency flattening onto black or white backgrounds.
- **All-in-One ICO Pipeline:** Pack single images or entire folders into multi-resolution `.ico` containers with optional black/white background removal.
- **Transparent PNG & WebP Exporting:** Remove solid backgrounds from single files or whole directories and save directly as transparent PNG or lightweight WebP assets.
- **Two-Way Image Compositing:** Center foreground icons onto base backgrounds (or stamp one logo onto an entire folder of backgrounds) with proportional scaling and multi-format export.
- **Next-Gen WebP Compression:** Converts heavy PNG/JPG assets into lightweight `.webp` files with real-time storage savings calculation.
- **Aspect-Ratio & Safety Protections:** Squaring scripts feature automated upscaling prevention to block blurry distortion, alongside batch volume confirmation prompts.

## Prerequisites
The scripts require Python 3, **Pillow**, and the **Click** library. Install all dependencies via your terminal:
```bash
pip install Pillow click
```

---

## 🚀 Included Scripts

### 1. `batch_strip_exif.py` (EXIF Metadata Inspector & Stripper)
Inspects hidden EXIF/metadata tags (`--inspect`) or permanently removes sensitive metadata (GPS location, camera info, timestamps, software tags) from a single image or an entire folder (`all`) while preserving visual orientation.
```bash
python batch_strip_exif.py <target_input> [-i | --inspect] [-f]

# Examples:
python batch_strip_exif.py all --inspect
python batch_strip_exif.py photo.jpg
```

### 2. `batch_color_filter.py` (Single & Bulk Color Filter)
Applies monochrome tinting, special modes (`grayscale`, `sepia`, `bitmap`, `lineart`), or two-tone Cyberpunk duotone color grading to a single image or an entire folder (`all`) while preserving alpha transparency. Reads and updates custom color presets in `colors.json`.
```bash
python batch_color_filter.py <target_input> [-t TINT | -d SHADOW HIGHLIGHT] [-i INTENSITY] [--list-colors] [--add-color NAME HEX] [-f]

# Examples:
python batch_color_filter.py --list-colors
python batch_color_filter.py --add-color lava "#FF3300"
python batch_color_filter.py icon.png --tint lava
python batch_color_filter.py photo.jpg --tint bitmap
python batch_color_filter.py all --duotone deepviolet neon -i 85
```

### 3. `batch_watermark.py` (Single & Bulk Text/Logo Watermarker)
Applies customizable text or transparent logo watermarks to a single image or an entire folder (`all`). Supports proportional scaling, edge margin control, opacity adjustment, custom text colors, and 5 anchor positions (`bottom-right`, `bottom-left`, `top-right`, `top-left`, `center`).
```bash
python batch_watermark.py <target_input> [-t TEXT | -l LOGO] [-p POS] [-s SCALE] [-m MARGIN] [-o OPACITY] [-c COLOR] [-f]

# Examples:
python batch_watermark.py wallpaper.jpg --text "© Don InFerno" --color cyan
python batch_watermark.py all --logo signature.png -p bottom-left -s 20 -o 90
```

### 4. `batch_convert.py` (Single & Bulk Raster Format Converter)
Converts a single image or an entire folder (`all`) between `png`, `jpg`, `webp`, `bmp`, `tiff`, and `gif` formats. Automatically flattens alpha transparency onto a solid `white` (default) or `black` background when converting to JPG or BMP.
```bash
python batch_convert.py <target_input> <target_format> [-b BG_COLOR] [-q QUALITY] [-f]

# Examples:
python batch_convert.py neon_logo.png jpg --bg black
python batch_convert.py all webp -q 85
```

### 5. `batch_ico.py` (Single & Bulk ICO Generator)
Packs a single image or an entire folder (`all`) into multi-resolution Windows `.ico` containers (16x16 up to 256x256). Optionally removes solid `black` or `white` backgrounds smoothly before packing and supports all major raster formats (`png`, `jpg`, `webp`, `bmp`, `tiff`, `gif`).
```bash
python batch_ico.py <target_input> [-b BG_COLOR] [--png] [-f]

# Examples:
python batch_ico.py ready_logo.png
python batch_ico.py all -b black --png
```

### 6. `batch_remove_bg.py` (Single & Bulk Transparent Background Remover)
Removes solid `black` (or `1`) or `white` (or `2`) backgrounds smoothly from a single image or an entire folder (`all`). Exports results as transparent PNG (default) or lightweight transparent WebP files (`--webp`).
```bash
python batch_remove_bg.py <mode> <target_input> [--webp] [-f]

# Examples:
python batch_remove_bg.py black neon_logo.png
python batch_remove_bg.py 1 all --webp
```

### 7. `batch_overlay.py` (Two-Way Image Overlay Compositor)
Places a foreground image dead-center onto a base background image. Supports `all` in either position (`all base.png` or `logo.png all`), proportional downscaling, relative size locking to the base image, and multiple raster export formats (`png`, `jpg`, `webp`).
```bash
python batch_overlay.py <foreground_input> <base_input> [-s SCALE] [-l] [--format FORMAT] [-f]

# Example:
python batch_overlay.py logo.png all -l -s 50
```

### 8. `batch_compress.py` (Single & Bulk WebP Optimizer)
Converts and compresses JPG, JPEG, and PNG images into the modern, lightweight `.webp` format while preserving transparency and resolution. Calculates total disk space saved in real time.
```bash
python batch_compress.py <target_input> [-q QUALITY] [-f]

# Example:
python batch_compress.py all -q 85
```

### 9. `batch_crop_resize.py` (Center-Crop Square Resizer)
Forces a single image or an entire folder (`all`) into a perfect square by scaling the shorter side and automatically cropping out any overflowing margins from the center. Features automated upscaling prevention and optional JPG export.
```bash
python batch_crop_resize.py <size> <target_input> [-f] [--jpg]

# Example:
python batch_crop_resize.py 1024 all --jpg
```

### 10. `batch_pad_resize.py` (Padded Square Resizer)
Resizes a single image or an entire folder (`all`) into a perfect square size without stretching, padding the empty margins with transparent, black, or white canvas space instead. Includes upscale prevention.
```bash
python batch_pad_resize.py <size> <target_input> [-f] [--black] [--white]

# Example:
python batch_pad_resize.py 1024 all --white
```

---

## 📚 Additional Documentation & Config
- **`colors.json`**: External JSON configuration file storing customizable hex color presets for `batch_color_filter.py`.
- **`Digital_Image_File_Formats_Guide.pdf`**: A reference guide explaining the technical differences between major Raster (`PNG`, `JPG`, `WebP`, `ICO`, `BMP`, `TIFF`, `GIF`) and Vector (`SVG`, `AI`, `EPS`) image formats.

## License
This project is open-source and free to use.
