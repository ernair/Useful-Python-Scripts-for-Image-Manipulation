"""
Batch & Single Automated AI Face Blur / Pixelate Tool (via Click & OpenCV YuNet)
================================================================================
Automatically detects human faces in single images or entire directories ('all') 
using OpenCV's YuNet ONNX deep learning model and obscures them with adaptive 
Gaussian blurring or mosaic pixelation. Supports smooth feathered oval masks 
(--shape oval) or classic rectangular boxes (--shape rect).

Automatically skips images where 0 faces are detected to prevent duplicate files.
Supports all major raster formats: JPG, JPEG, PNG, WebP, BMP, TIFF, and GIF.

Prerequisites:
    pip install opencv-python numpy Pillow click

Usage:
    python batch_faceblur.py <target_input> [options]

Examples:
    python batch_faceblur.py photo.jpg
    python batch_faceblur.py all --shape oval --strength 1.2
    python batch_faceblur.py group.png --pixelate --shape rect
    python batch_faceblur.py crowd.jpg --confidence 0.6 -f
"""

import os
import urllib.request
import cv2
import numpy as np
import click
from PIL import Image
import subprocess 

MODEL_FILENAME = "face_detection_yunet_2023mar.onnx"
MODEL_URL = (
    "https://"
    "://githubusercontent.com"
    "opencv/opencv_zoo/main/models/face_detection_yunet/"
    + MODEL_FILENAME
)

def ensure_yunet_model():
    """Checks for a valid YuNet ONNX model next to the script and downloads it via curl if missing."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, MODEL_FILENAME)
    
    is_valid = False
    if os.path.exists(model_path) and os.path.getsize(model_path) > 100000:
        with open(model_path, 'rb') as f:
            if not f.read(64).lstrip().startswith(b'<'):
                is_valid = True

    if not is_valid:
        if os.path.exists(model_path):
            os.remove(model_path)
        click.secho(f"Downloading YuNet ONNX face detection model ({MODEL_FILENAME})...", fg='cyan')
        try:
            # Use system curl (built into Windows 10/11, macOS, Linux) to bypass Python urllib proxy issues
            cmd = ["curl", "-L", "-f", "-s", "-o", model_path, MODEL_URL]
            res = subprocess.run(cmd)
            
            if res.returncode != 0 or not os.path.exists(model_path) or os.path.getsize(model_path) < 100000:
                if os.path.exists(model_path):
                    os.remove(model_path)
                raise click.ClickException(
                    f"Auto-download failed. Please place '{MODEL_FILENAME}' manually in the script folder."
                )
            click.secho("Model downloaded successfully!", fg='green')
        except Exception as e:
            if os.path.exists(model_path):
                os.remove(model_path)
            raise click.ClickException(str(e))
            
    return model_path

def apply_pixelate(roi, blocks=12):
    """Applies a mosaic pixelation effect to a BGR image sub-region."""
    h, w = roi.shape[:2]
    if w < 2 or h < 2:
        return roi
    small_w = max(2, min(w, blocks))
    small_h = max(2, min(h, int(blocks * (h / float(w)))))
    temp = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

def obscure_faces_in_image(pil_img, model_path, shape, strength, pixelate, confidence):
    """Detects faces via YuNet and obscures them with oval/rect blur or pixelation.
    Returns (processed_pil_image, detected_face_count).
    """
    orig_rgba = pil_img.convert("RGBA")
    r, g, b, alpha = orig_rgba.split()
    
    rgb_np = np.array(orig_rgba.convert("RGB"))
    bgr_img = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2BGR)
    img_h, img_w = bgr_img.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        model=model_path,
        config="",
        input_size=(img_w, img_h),
        score_threshold=confidence,
        nms_threshold=0.3,
        top_k=5000,
    )

    _, faces = detector.detect(bgr_img)
    if faces is None or len(faces) == 0:
        return pil_img, 0

    output_bgr = bgr_img.copy()
    detected_count = 0

    for face in faces:
        x, y, box_w, box_h = map(int, face[:4])
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img_w, x + box_w)
        y2 = min(img_h, y + box_h)

        roi_w = x2 - x1
        roi_h = y2 - y1
        # Ignore tiny noise/false-positive detections smaller than 24x24 pixels
        if roi_w < 24 or roi_h < 24:
            continue

        detected_count += 1
        sub_roi = bgr_img[y1:y2, x1:x2]

        if pixelate:
            block_count = max(4, int(round(14 / strength)))
            obscured_roi = apply_pixelate(sub_roi, blocks=block_count)
        else:
            k_w = int((roi_w / 3.0) * strength) | 1
            k_h = int((roi_h / 3.0) * strength) | 1
            k_w = max(3, k_w)
            k_h = max(3, k_h)
            obscured_roi = cv2.GaussianBlur(sub_roi, (k_w, k_h), 0)

        if shape == 'rect':
            output_bgr[y1:y2, x1:x2] = obscured_roi
        else:
            mask = np.zeros((roi_h, roi_w), dtype=np.uint8)
            center = (roi_w // 2, roi_h // 2)
            axes = (max(1, int(roi_w * 0.48)), max(1, int(roi_h * 0.48)))
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

            feather_k = int(min(roi_w, roi_h) * 0.18) | 1
            feather_k = max(3, feather_k)
            mask_blurred = cv2.GaussianBlur(mask, (feather_k, feather_k), 0)

            alpha_mask = (mask_blurred.astype(np.float32) / 255.0)[:, :, np.newaxis]
            blended_roi = (obscured_roi.astype(np.float32) * alpha_mask + sub_roi.astype(np.float32) * (1.0 - alpha_mask))
            output_bgr[y1:y2, x1:x2] = blended_roi.astype(np.uint8)

    final_rgb = cv2.cvtColor(output_bgr, cv2.COLOR_BGR2RGB)
    final_pil = Image.fromarray(final_rgb).convert("RGBA")
    final_pil.putalpha(alpha)
    return final_pil, detected_count

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('--shape', type=click.Choice(['oval', 'rect'], case_sensitive=False), default='oval', show_default=True, help='Shape of the obscured region: feathered oval or sharp rectangle.')
@click.option('-s', '--strength', type=click.FloatRange(0.2, 4.0), default=1.0, show_default=True, help='Blur or pixelation intensity multiplier (1.0 = default).')
@click.option('--pixelate', is_flag=True, help='Use mosaic pixelation instead of smooth Gaussian blur.')
@click.option('-c', '--confidence', type=click.FloatRange(0.1, 0.95), default=0.75, show_default=True, help='AI face detection score threshold (lower = detects smaller/distant faces).')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt for large batches (more than 5 files).')
def blur_faces(target_input, shape, strength, pixelate, confidence, force):
    """Automated AI Face Blur & Pixelation Tool.
    
    Detects human faces using OpenCV's YuNet neural network and obscures them 
    in a single image or an entire directory ('all'). Skips images with 0 faces.
    
    Supports all major raster formats: JPG, JPEG, PNG, WebP, BMP, TIFF, and GIF.
    """
    os.environ["OPENCV_LOG_LEVEL"] = "OFF"
    model_path = ensure_yunet_model()

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    files_to_process = tuple()
    shape_mode = shape.lower()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            f for f in os.listdir(current_dir)
            if f.lower().endswith(valid_extensions)
            and '_blurred.' not in f.lower()
        )
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to scan for faces.")
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to process a large batch ({len(files_to_process)} files).", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
            click.echo("Proceeding with batch face blurring...")
        elif force:
            click.echo("Force flag (-f/--force) detected. Bypassing safety prompts...")
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        if not target_input.lower().endswith(valid_extensions):
            click.secho(f"Error: Unsupported file format. Supported: {', '.join(valid_extensions)}", fg='red', bold=True)
            return
        files_to_process = (target_input,)

    effect_desc = "Pixelate" if pixelate else "Gaussian Blur"
    click.echo(f"\n--- Running AI Face Obscuring ({effect_desc} | Shape: {shape_mode} | Strength: {strength}x | Confidence: {confidence}) ---")
    success_count = 0
    total_faces = 0

    for file_name in files_to_process:
        file_name_without_ext, orig_ext = os.path.splitext(file_name)
        orig_ext_lower = orig_ext.lower()
        
        if orig_ext_lower in ('.jpg', '.jpeg'):
            out_ext = '.jpg'
            out_path = f"{file_name_without_ext}_blurred{out_ext}"
        elif orig_ext_lower == '.webp':
            out_ext = '.webp'
            out_path = f"{file_name_without_ext}_blurred{out_ext}"
        elif orig_ext_lower == '.png':
            out_ext = '.png'
            out_path = f"{file_name_without_ext}_blurred{out_ext}"
        else:
            out_ext = '.png'
            ext_tag = orig_ext_lower.lstrip('.')
            out_path = f"{file_name_without_ext}_{ext_tag}_blurred{out_ext}"

        try:
            click.echo(f"Scanning '{file_name}'...")
            with Image.open(file_name) as img:
                result_img, face_count = obscure_faces_in_image(
                    img, model_path, shape_mode, strength, pixelate, confidence
                )
                
                if face_count == 0:
                    click.secho("  -> 0 faces detected. Skipped.", fg='yellow')
                    continue
                else:
                    click.secho(f"  -> Detected and obscured {face_count} face(s).", fg='green')
                    total_faces += face_count

                if os.path.exists(out_path):
                    os.remove(out_path)

                if out_ext == '.jpg':
                    result_img.convert("RGB").save(out_path, format="JPEG", quality=95)
                elif out_ext == '.webp':
                    result_img.save(out_path, format="WEBP", quality=90, method=6)
                else:
                    result_img.save(out_path, format="PNG")

                click.secho(f"  -> Saved: {out_path}", fg='cyan')
                success_count += 1
        except Exception as e:
            click.secho(f"  -> Failed to process '{file_name}': {e}", fg='red', bold=True)

    click.secho(f"\nFinished! Processed {success_count}/{len(files_to_process)} image(s) ({total_faces} total face(s) obscured).", fg='green', bold=True)

if __name__ == "__main__":
    blur_faces()
