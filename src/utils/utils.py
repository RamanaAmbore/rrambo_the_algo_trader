import shutil
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

import pandas as pd
import pyotp


def generate_totp(totp_key):
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(totp_key).now()


def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with 4 decimal places for option Greeks."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


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


def read_file_content(file_path, file_extension):
    """
    Reads the content of a file based on its extension.

    :param file_path: Path to the file.
    :param file_extension: File extension (.txt, .csv, .xlsx).
    :return: File content as a string for .txt/.csv, or DataFrame for .xlsx.
    """
    try:
        if file_extension == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_extension == "csv":
            return pd.read_csv(file_path)  # Return CSV as a string
        elif file_extension == "xlsx":
            return pd.read_excel(file_path)  # Return Excel as a string
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""
