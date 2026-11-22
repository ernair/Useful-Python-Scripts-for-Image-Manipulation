"""
Batch & Single Workflow Pipeline Runner (via Click)
===================================================
Chains multiple image manipulation scripts together into reusable, named 
workflows stored in an external 'pipelines.json' file. Automatically tracks 
output filenames between steps, supports single files or 'all', cleans up 
intermediate files, and allows custom output suffix tagging (--tag).

Prerequisites:
    pip install Pillow click

Usage:
    python batch_pipeline.py <pipeline_name> <target_input> [options]

Examples:
    python batch_pipeline.py --list
    python batch_pipeline.py --save ico_prosessi "batch_convert.py {file} png" "batch_trim.py {file} --auto -b black -p 1 -r" "batch_ico.py {file}"
    python batch_pipeline.py --delete ico_prosessi
    python batch_pipeline.py ico_prosessi kuva.jpg --tag auto
    python batch_pipeline.py ico_prosessi all -t final
"""

import os
import sys
import json
import shlex
import subprocess
import click

def get_script_dir():
    """Returns the directory where batch_pipeline.py is located."""
    return os.path.dirname(os.path.abspath(__file__))

def get_pipelines_path():
    """Returns the absolute path to 'pipelines.json'."""
    return os.path.join(get_script_dir(), 'pipelines.json')

def load_pipelines():
    """Loads saved workflows from 'pipelines.json', creating a starter file if missing."""
    json_path = get_pipelines_path()
    default_pipelines = {
        "ico_prosessi": {
            "description": "Convert to PNG, auto-trim black borders, and pack into Windows ICO",
            "steps": (
                "batch_convert.py {file} png",
                "batch_trim.py {file} --auto -b black -p 1 -r",
                "batch_ico.py {file}"
            )
        }
    }
    
    if not os.path.exists(json_path):
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(default_pipelines, f, indent=4)
        except Exception:
            pass
        return default_pipelines

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else default_pipelines
    except Exception as e:
        click.secho(f"[Warning] Could not read pipelines.json ({e}). Using defaults.", fg='yellow')
        return default_pipelines

def save_pipeline(name, steps, description=""):
    """Saves or updates a named workflow in 'pipelines.json'."""
    clean_name = name.strip().lower()
    if not clean_name:
        raise click.BadParameter("Pipeline name cannot be empty.")
    if not steps:
        raise click.BadParameter("You must provide at least one command step.")

    pipelines = load_pipelines()
    existed = clean_name in pipelines
    
    pipelines[clean_name] = {
        "description": description.strip() if description else "Custom user workflow",
        "steps": tuple(s.strip() for s in steps if s.strip())
    }
    
    json_path = get_pipelines_path()
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(pipelines, f, indent=4)
        
    return clean_name, existed

def delete_pipeline(name):
    """Deletes a named workflow from 'pipelines.json'."""
    clean_name = name.strip().lower()
    if not clean_name:
        raise click.BadParameter("Provide the name of the workflow to delete.")

    pipelines = load_pipelines()
    if clean_name not in pipelines:
        raise click.BadParameter(f"Workflow '{clean_name}' was not found in pipelines.json.")

    del pipelines[clean_name]
    
    json_path = get_pipelines_path()
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(pipelines, f, indent=4)
        
    return clean_name

def detect_newest_output(dir_path, before_snapshot, current_file):
    """Detects the newly created or modified file produced by a pipeline step."""
    after_snapshot = {}
    for f in os.listdir(dir_path):
        full_p = os.path.join(dir_path, f)
        if os.path.isfile(full_p):
            after_snapshot[f] = os.path.getmtime(full_p)
            
    new_files = tuple(f for f in after_snapshot if f not in before_snapshot)
    if new_files:
        non_ico = tuple(f for f in new_files if not f.lower().endswith('.ico'))
        candidates = non_ico if non_ico else new_files
        return max(candidates, key=lambda f: after_snapshot[f])
        
    updated_files = tuple(
        f for f, mtime in after_snapshot.items()
        if f in before_snapshot and mtime > before_snapshot[f] and f != current_file
    )
    if updated_files:
        return max(updated_files, key=lambda f: after_snapshot[f])
        
    return current_file

# --- CLICK CLI CONFIGURATION ---

@click.command()
@click.argument('pipeline_name', required=False)
@click.argument('target_input', required=False)
@click.option('--list', 'list_mode', is_flag=True, help='List all saved workflows from pipelines.json and exit.')
@click.option('--save', 'save_mode', is_flag=True, help='Save a new workflow: --save <name> "<step1>" "<step2>" ...')
@click.option('--delete', 'delete_mode', is_flag=True, help='Delete a saved workflow: --delete <name>')
@click.option('--desc', default="", help='Optional description when saving a new workflow with --save.')
@click.option('-t', '--tag', default=None, help="Rename final output as '<orig>_<tag>.<ext>' (use 'auto' for pipeline name).")
@click.option('--keep-temp', is_flag=True, help='Keep intermediate files created between steps instead of deleting them.')
@click.option('-f', '--force', is_flag=True, help='Bypass confirmation prompt for large batches (more than 5 files).')
@click.argument('extra_steps', nargs=-1)
def run_pipeline(pipeline_name, target_input, list_mode, save_mode, delete_mode, desc, tag, keep_temp, force, extra_steps):
    """Batch & Single Image Workflow Pipeline Runner.
    
    Executes a saved sequence of image scripts from 'pipelines.json' on a 
    single file or an entire folder ('all'). Automatically passes each step's 
    output file into the next step.
    """
    pipelines = load_pipelines()

    # --- MODE 1: LIST WORKFLOWS ---
    if list_mode:
        click.secho("\n--- Saved Workflows (from pipelines.json) ---", fg='cyan', bold=True)
        if not pipelines:
            click.secho("  No workflows saved yet. Use --save to create one.", fg='yellow')
        else:
            for name, info in pipelines.items():
                click.secho(f"\n  * {name}", fg='green', bold=True)
                if info.get("description"):
                    click.echo(f"    Description: {info['description']}")
                for idx, step in enumerate(info.get("steps", ()), start=1):
                    click.echo(f"      {idx}. {step}")
        click.echo("")
        return

    # --- MODE 2: SAVE NEW WORKFLOW ---
    if save_mode:
        if not pipeline_name:
            click.secho("Error: Provide a workflow name after --save (e.g., --save my_flow \"step1\" \"step2\").", fg='red', bold=True)
            return
        all_steps = ()
        if target_input:
            all_steps = all_steps + (target_input,)
        if extra_steps:
            all_steps = all_steps + tuple(extra_steps)
            
        try:
            saved_name, existed = save_pipeline(pipeline_name, all_steps, desc)
            action = "Updated" if existed else "Saved"
            click.secho(f"Success! {action} workflow '{saved_name}' with {len(all_steps)} step(s) in pipelines.json.", fg='green', bold=True)
        except click.BadParameter as bp:
            click.secho(f"Error: {bp.format_message()}", fg='red', bold=True)
        return

    # --- MODE 3: DELETE WORKFLOW ---
    if delete_mode:
        if not pipeline_name:
            click.secho("Error: Provide a workflow name after --delete (e.g., --delete my_flow).", fg='red', bold=True)
            return
        try:
            deleted_name = delete_pipeline(pipeline_name)
            click.secho(f"Deleted workflow '{deleted_name}' from pipelines.json.", fg='yellow', bold=True)
        except click.BadParameter as bp:
            click.secho(f"Error: {bp.format_message()}", fg='red', bold=True)
        return

    # --- MODE 4: EXECUTE WORKFLOW ---
    if not pipeline_name or not target_input:
        click.secho("Error: Provide <PIPELINE_NAME> and <TARGET_INPUT>, or use --list / --save / --delete.", fg='red', bold=True)
        return

    clean_key = pipeline_name.strip().lower()
    if clean_key not in pipelines:
        click.secho(f"Error: Workflow '{pipeline_name}' not found in pipelines.json. Use --list to see available workflows.", fg='red', bold=True)
        return

    steps = pipelines[clean_key].get("steps", ())
    if not steps:
        click.secho(f"Error: Workflow '{clean_key}' has no steps defined.", fg='red', bold=True)
        return

    # Resolve final suffix tag if requested
    resolved_tag = None
    if tag:
        resolved_tag = clean_key if tag.strip().lower() == 'auto' else tag.strip()

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif')
    current_dir = os.getcwd()
    script_dir = get_script_dir()
    files_to_process = tuple()

    if target_input.lower() == 'all':
        files_to_process = tuple(
            sorted(f for f in os.listdir(current_dir) if f.lower().endswith(valid_extensions))
        )
        if not files_to_process:
            click.secho("No supported raster images found in this folder.", fg='yellow')
            return

        click.echo(f"Found {len(files_to_process)} image(s) for workflow '{clean_key}'.")
        CRITICAL_LIMIT = 5
        if len(files_to_process) > CRITICAL_LIMIT and not force:
            click.secho(f"\n[WARNING] You are about to run a {len(steps)}-step workflow on {len(files_to_process)} files.", fg='yellow', bold=True)
            if not click.confirm("Are you sure you want to proceed?"):
                click.echo("Operation cancelled by user.")
                return
    else:
        if not os.path.exists(target_input):
            click.secho(f"Error: The file '{target_input}' was not found.", fg='red', bold=True)
            return
        files_to_process = (target_input,)

    click.secho(f"\n=== Running Workflow: '{clean_key}' ({len(steps)} steps) ===", fg='cyan', bold=True)
    success_count = 0

    for orig_file in files_to_process:
        click.secho(f"\nProcessing '{orig_file}':", fg='white', bold=True)
        current_file = orig_file
        intermediate_files = ()
        step_failed = False

        for step_idx, raw_step in enumerate(steps, start=1):
            before_snap = {
                f: os.path.getmtime(os.path.join(current_dir, f))
                for f in os.listdir(current_dir)
                if os.path.isfile(os.path.join(current_dir, f))
            }

            tokens = shlex.split(raw_step, posix=False)
            if not tokens:
                continue

            parsed_tokens = ()
            for tok in tokens:
                stripped = tok.strip('"').strip("'")
                if '{file}' in stripped:
                    stripped = stripped.replace('{file}', current_file)
                parsed_tokens = parsed_tokens + (stripped,)

            script_name, *script_args_list = parsed_tokens
            script_args = tuple(script_args_list)

            if os.path.exists(script_name):
                script_path = script_name
            else:
                candidate = os.path.join(script_dir, script_name)
                script_path = candidate if os.path.exists(candidate) else script_name

            cmd = (sys.executable, script_path) + script_args
            click.echo(f"  [Step {step_idx}/{len(steps)}] Running: {script_name} {' '.join(script_args)}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                click.secho(f"  -> Step {step_idx} failed! Output:\n{result.stderr or result.stdout}", fg='red')
                step_failed = True
                break

            next_file = detect_newest_output(current_dir, before_snap, current_file)
            if next_file != current_file:
                if current_file != orig_file and current_file not in intermediate_files:
                    intermediate_files = intermediate_files + (current_file,)
                current_file = next_file

        if not step_failed:
            if not keep_temp and intermediate_files:
                for tmp_f in intermediate_files:
                    if tmp_f != current_file and os.path.exists(tmp_f):
                        try:
                            os.remove(tmp_f)
                        except Exception:
                            pass

            # Rename final output using --tag if specified and a new file was produced
            if resolved_tag and current_file != orig_file and os.path.exists(current_file):
                orig_base, _ = os.path.splitext(os.path.basename(orig_file))
                _, final_ext = os.path.splitext(current_file)
                tagged_name = f"{orig_base}_{resolved_tag}{final_ext}"
                if tagged_name != current_file:
                    if os.path.exists(tagged_name):
                        os.remove(tagged_name)
                    os.rename(current_file, tagged_name)
                    current_file = tagged_name

            click.secho(f"  -> Completed! Final output: {current_file}", fg='green')
            success_count += 1

    click.secho(f"\nWorkflow '{clean_key}' finished! Successfully processed {success_count}/{len(files_to_process)} file(s).", fg='green', bold=True)

if __name__ == "__main__":
    run_pipeline()
