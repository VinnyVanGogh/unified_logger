import os
import json
import hashlib

from .constants import OUTPUT_DIR_NAME


def write_json_to_file(file_path, data):
    """
    Write a dictionary to a file in JSON format.

    Args:
        file_path (str): The path to the file where the JSON data will be written.
        data (dict): The dictionary data to be written to the file.

    Returns:
        None
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_output_dir_path(dir: str = None) -> str:
    """
    Get the path to the output directory, creating it if it doesn't exist.

    Args:
        dir (str, optional): The path to the output directory. If not provided, 
                             the default directory is created in the current working directory.

    Returns:
        str: The path to the output directory.
    """
    if not dir:
        dir = os.path.join(os.getcwd(), OUTPUT_DIR_NAME)
   
    os.makedirs(dir, exist_ok=True)
    return dir

def calculate_hash(file_path: str, hash_type: str) -> str:
    """
    Calculate the hash of a file using the specified hash algorithm.

    Args:
        file_path (str): The path to the file to be hashed.
        hash_type (str): The type of hash algorithm to use (e.g., 'sha256', 'md5').

    Returns:
        str: The hexadecimal digest of the file's hash.
    """
    hash_obj = hashlib.new(hash_type)
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def calculate_directory_files_hash(directory: str, hash_type: str) -> dict:
    """
    Calculate the hash for all files in a given directory using the specified hash algorithm.

    Args:
        directory (str): The path to the directory containing the files to be hashed.
        hash_type (str): The type of hash algorithm to use (e.g., 'sha256', 'md5').

    Returns:
        dict: A dictionary where the keys are filenames and the values are their corresponding hash values.
    """
    hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            hash_value = calculate_hash(file_path, hash_type)
            hashes[file] = hash_value
    return hashes
