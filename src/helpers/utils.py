import shutil
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

import pandas as pd
import pyotp


def generate_totp(totp_key):
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(totp_key).now()


def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with specified precision."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


def delete_folder_contents(folder_path):
    """Deletes all files and subdirectories inside the specified folder."""
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        print(f"Folder '{folder_path}' does not exist or is not a directory.")
        return False

    success = True
    for item in folder.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Failed to delete {item}: {e}")
            success = False
    return success


def read_file_content(file_path, file_extension):
    """Reads the content of a file based on its extension."""
    try:
        if file_extension == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_extension == "csv":
            return pd.read_csv(file_path)  # Convert DataFrame to string
        elif file_extension == "xlsx":
            return pd.read_excel(file_path)  # Convert DataFrame to string
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


def parse_value(value: str, target_type: type = None):
    """Converts a string into its appropriate data type or a specified type."""

    if value is None: return None
    value = value.strip()
    if value == 'None': return None

    if value == "":
        return ""  # Return empty string for empty input

    if target_type:
        try:
            if target_type is bool:
                return value.lower() == "true"
            return target_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{value}' to {target_type.__name__}")

    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    if value.isdigit() or (value[0] in "+-" and value[1:].isdigit()):
        return int(value)

    try:
        return float(value)
    except ValueError:
        return value


def create_instr_symbol_xref(data, xref, reverse_key=None, use_type=set):
    symbol_id_xref = reverse_dict(data, reverse_key, use_type)
    instr_id_xref = {}
    for key, val in symbol_id_xref.items():
        instr_id_xref[xref[key]['instrument_token']] = val
    return symbol_id_xref, instr_id_xref


def reverse_dict(data, reverse_key=None, use_type=set):
    if use_type is None:
        multi_set_dict = dict()
    else:
        multi_set_dict = defaultdict(use_type)

    for key, val in data.items():
        temp_key = val[reverse_key]
        if use_type is None:
            multi_set_dict[temp_key] = key
        else:
            multi_set_dict[temp_key].add(key)

    if use_type is None:
        return multi_set_dict
    else:
        return dict(multi_set_dict)
