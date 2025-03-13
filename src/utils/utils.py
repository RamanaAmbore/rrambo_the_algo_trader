import os
import re
from decimal import Decimal, ROUND_DOWN

import pyotp


def generate_totp(totp_key):
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(totp_key).now()


def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with 4 decimal places for option Greeks."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


import shutil
from pathlib import Path


def delete_folder_contents(folder_path):
    """
    Deletes all files and subdirectories inside the specified folder.
    If the folder does not exist or is not a directory, it prints a message and exits.

    :param folder_path: Path to the folder whose contents need to be deleted.
    """
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        print(f"The folder '{folder_path}' does not exist or is not a directory.")
        return

    for item in folder.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()  # Delete file or symlink
            elif item.is_dir():
                shutil.rmtree(item)  # Delete directory and its contents
            print(f"Deleted: {item}")
        except Exception as e:
            print(f"Failed to delete {item}: {e}")


def list_files_by_regex_patterns(folder_path, regex_patterns):
    """
    List files from a folder and match them against multiple regex patterns.

    :param folder_path: Path to the folder containing files.
    :param regex_patterns: List of regex patterns to match files.
    :return: List of lists, where each inner list contains files matching a regex pattern.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")

    # Get all files in the folder
    all_files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # Match files for each regex pattern
    matched_files = []
    for pattern in regex_patterns:
        compiled_pattern = re.compile(pattern)
        matched_files.append([file for file in all_files if compiled_pattern.match(file)])

    return matched_files


