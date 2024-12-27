#!/usr/bin/env python3

import os
import sys
import shutil

def list_files(base_path, recursive=False):
    """
    Lists files in the given base_path.
    If recursive is True, it walks subdirectories.
    Returns a list of absolute file paths.
    """
    file_list = []
    if recursive:
        for root, dirs, files in os.walk(base_path):
            for f in files:
                file_list.append(os.path.join(root, f))
    else:
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isfile(full_path):
                file_list.append(full_path)
    return file_list


def prompt_user_for_action(file_path, base_path):
    """
    Prompts the user for how to move/rename/skip the file.
    Returns a tuple of (target_directory, new_filename) or None if skipped.
    """
    print(f"\nFile: {file_path}")

    # Ask user whether they want to move this file
    move_choice = input(
        "Enter subfolder name to move, "
        "or 'skip' to skip, "
        "or 'rename' to rename the file.\n> "
    ).strip()

    # If user chooses to skip
    if move_choice.lower() == "skip":
        return None

    # If user chooses to rename
    if move_choice.lower() == "rename":
        new_name = input("Enter new name (with extension): ").strip()
        # By default, assume they want to move it in the same base directory
        return (base_path, new_name)

    # Otherwise, user gave us a subfolder name
    new_subfolder = move_choice
    # We can also optionally allow them to rename the file in this new subfolder
    rename_choice = input("Do you want to rename the file? (y/n): ").strip().lower()
    if rename_choice == 'y':
        new_name = input("Enter new name (with extension): ").strip()
        return (os.path.join(base_path, new_subfolder), new_name)
    else:
        # Keep the original file name
        original_filename = os.path.basename(file_path)
        return (os.path.join(base_path, new_subfolder), original_filename)


def confirm_and_move(actions):
    """
    Summarizes the user decisions and asks for final confirmation.
    Then performs the moves if the user confirms.
    """
    if not actions:
        print("\nNo files selected for moving. Exiting.")
        return

    print("\nSummary of planned actions:")
    for src, (dest_dir, dest_filename) in actions.items():
        print(f"  Move: {src}")
        print(f"   To: {os.path.join(dest_dir, dest_filename)}")
    print()

    proceed = input("Proceed with these moves? (Y/N): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled.")
        return

    # Proceed with moves
    for src, (dest_dir, dest_filename) in actions.items():
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        destination = os.path.join(dest_dir, dest_filename)

        # Handle potential collision
        if os.path.exists(destination):
            print(f"[Collision] File already exists at {destination}")
            choice = input("Overwrite (o), Rename (r), or Skip (s)? ").strip().lower()
            if choice == 'o':
                pass  # proceed, will overwrite
            elif choice == 'r':
                new_name = input("Enter new filename: ").strip()
                destination = os.path.join(dest_dir, new_name)
            else:
                print("Skipping this file.")
                continue

        try:
            shutil.move(src, destination)
            print(f"[Moved] {src} -> {destination}")
        except Exception as e:
            print(f"[Error] Could not move {src} to {destination}. Reason: {e}")


def main():
    # --- Argument parsing ---
    if len(sys.argv) < 2:
        print("Usage: python sort_cli.py <directory> [--recursive]")
        sys.exit(1)

    base_path = sys.argv[1]
    if not os.path.isdir(base_path):
        print(f"Error: {base_path} is not a valid directory.")
        sys.exit(1)

    recursive = False
    if len(sys.argv) > 2 and sys.argv[2] == "--recursive":
        recursive = True

    # --- List files ---
    files = list_files(base_path, recursive=recursive)
    if not files:
        print("No files found in the specified directory.")
        sys.exit(0)

    print(f"Found {len(files)} file(s) in {base_path} (recursive={recursive}).")

    # --- Prompt user actions for each file ---
    actions = {}  # key: src file, value: (dest_directory, new_filename)
    for f in files:
        user_decision = prompt_user_for_action(f, base_path)
        if user_decision is not None:
            actions[f] = user_decision

    # --- Confirm and move ---
    confirm_and_move(actions)


if __name__ == "__main__":
    main()
