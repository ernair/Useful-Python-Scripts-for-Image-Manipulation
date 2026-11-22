"""
Batch & Single Image Smart File Renamer (via Click)
===================================================
Safely renames image files using sequential numbering (--prefix), filename 
sanitization (--clean: lowercase, underscores, no special characters), or 
substring replacement (--replace). Includes a safe two-pass rename engine 
to prevent accidental overwrites and a --dry-run preview mode.

Supports all major raster formats: PNG, JPG, JPEG, WebP, BMP, TIFF, GIF, and ICO.

Prerequisites:
    pip install click

Usage:
    python batch_rename.py <target_input> [options]

Examples:
    python batch_rename.py all --prefix cyber_icon --digits 3
    python batch_rename.py all --clean --dry-run
    python batch_rename.py all --replace "_trimmed" ""
    python batch_rename.py "My Photo (1).jpg" --clean
"""

import os
import re
import uuid
import click

def sanitize_filename(base_name):
    """Converts spaces/hyphens to underscores, removes special chars, and lowercases."""
    cleaned = base_name.strip().lower()
    # Replace spaces and hyphens with underscores
    cleaned = re.sub(r'[\s\-]+', '_', cleaned)
    # Remove any character that is not a-z, 0-9, or underscore
    cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
    # Collapse multiple consecutive underscores into one
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned if cleaned else "renamed_file"

def compute_new_names(files, prefix, start_num, digits, clean_mode, replace_pair):
    """Calculates target filenames without modifying disk yet. Returns list of (old, new) tuples."""
    plan = ()
    used_targets = set()
    counter = start_num

    for old_name in files:
        base_name, ext = os.path.splitext(old_name)
        ext_lower = ext.lower()
        new_base = base_name

        if clean_mode:
            new_base = sanitize_filename(new_base)

        if replace_pair:
            old_sub, new_sub = replace_pair
            new_base = new_base.replace(old_sub, new_sub)

        if prefix:
            clean_pref = prefix.strip()
            num_str = str(counter).zfill(digits)
            new_base = f"{clean_pref}_{num_str}"
            counter += 1

        if not new_base:
            new_base = "file"

        candidate = f"{new_base}{ext_lower}"

        # Prevent duplicate target names inside the same batch
        dup_idx = 2
        while candidate.lower() in used_targets:
            candidate = f"{new_base}_{dup_idx}{ext_lower}"
            dup_idx += 1

        used_targets.add(candidate.lower())
        plan = plan + ((old_name, candidate),)

    return plan

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('target_input')
@click.option('-p', '--prefix', default=None, help='Rename sequentially with a prefix (e.g., --prefix cyber_icon -> cyber_icon_001.png).')
@click.option('--start', 'start_num', type=int, default=1, show_default=True, help='Starting number when using --prefix.')
@click.option('--digits', type=click.IntRange(1, 6), default=3, show_default=True, help='Zero-padding digits for --prefix numbering (e.g., 3 -> 001).')
@click.option('--clean', 'clean_mode', is_flag=True, help='Sanitize filenames (lowercase, replace spaces with underscores, strip special chars).')
@click.option('--replace', 'replace_pair', nargs=2, default=None, help='Replace text in filenames (e.g., --replace "_trimmed" "").')
@click.option('--dry-run', is_flag=True, help='Preview all planned renames without modifying any files.')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt for large batches (more than 10 files).')
def rename_images(target_input, prefix, start_num, digits, clean_mode, replace_pair, dry_run, force):
    """Smart Single & Bulk Image File Renamer.
    
    Renames a single image or an entire folder ('all') using sequential numbering 
    (--prefix), filename sanitization (--clean), or text replacement (--replace).
    """
    if not prefix and not clean_mode and not replace_pair:
        click.secho("Error: Specify at least one action: --prefix, --clean, or --replace.", fg='red', bold=True)
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif', '.ico')
    current_dir = os.getcwd()
    files_to_process = tuple()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            sorted(f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions))
        )
        if not files_to_process:
            click.secho("No supported image files found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) to evaluate.")
        CRITICAL_LIMIT = 10
        if len(files_to_process) > CRITICAL_LIMIT and not force and not dry_run:
            click.secho(f"\n[WARNING] You are about to rename {len(files_to_process)} files.", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        files_to_process = (os.path.basename(target_input),)

    plan = compute_new_names(files_to_process, prefix, start_num, digits, clean_mode, replace_pair)
    changes = tuple((old, new) for old, new in plan if old != new)

    if not changes:
        click.secho("All filenames already match the target format. Nothing to rename.", fg='yellow')
        return

    if dry_run:
        click.secho(f"\n--- Dry Run Preview ({len(changes)} file(s) would be renamed) ---", fg='cyan', bold=True)
        for old_name, new_name in changes:
            click.echo(f"  {old_name}  -->  {new_name}")
        click.echo("\nNo files were modified. Remove --dry-run to apply changes.\n")
        return

    click.echo(f"\n--- Renaming {len(changes)} file(s) ---")
    # Two-pass rename via temporary UUIDs to avoid name collisions during batch renames
    temp_map = ()
    try:
        for old_name, new_name in changes:
            temp_name = f".tmp_rename_{uuid.uuid4().hex}_{old_name}"
            os.rename(old_name, temp_name)
            temp_map = temp_map + ((old_name, temp_name, new_name),)

        for old_name, temp_name, new_name in temp_map:
            if os.path.exists(new_name):
                click.secho(f"  [Skipped] Target '{new_name}' already exists; restoring '{old_name}'.", fg='yellow')
                os.rename(temp_name, old_name)
            else:
                os.rename(temp_name, new_name)
                click.secho(f"  {old_name}  -->  {new_name}", fg='cyan')

        click.secho("\nFinished! Batch rename completed safely.", fg='green', bold=True)
    except Exception as e:
        click.secho(f"\nError during rename operation: {e}", fg='red', bold=True)

if __name__ == "__main__":
    rename_images()
