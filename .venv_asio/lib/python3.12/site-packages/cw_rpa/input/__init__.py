"""
This module provides the Input class for handling input data.

The Input class is designed as a singleton to ensure only one instance
manages the input data throughout the application. It supports loading
data from a specified JSON file.
"""

import json
import os
import sys
import base64
from .constants import INPUT_FILE_NAME

__all__ = ["Input"]

class Input:  
    """
    The Input class is responsible for loading and providing access to input data.
    """

    _instance = None 
    _data: dict = {}

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the Input class if it doesn't already exist.
        """
        if cls._instance is None:
            cls._instance = super(Input, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):       
        """
        Initialize the Input instance by loading data from either command line arguments or a file.
        """
        if not self._data:           
            self.load_data()

    def load_data(self):
        """
        Load data from either command line arguments or a file.
        """
        if len(sys.argv) > 1:
            self._load_data_from_args()
        else:
            self._load_data_from_file()

    def _load_data_from_args(self):
        """
        Load data from command line arguments and decode it from base64.
        Raises:
            base64.binascii.Error: If there is an error while decoding base64 data from input arguments.
            json.JSONDecodeError: If there is an error while decoding JSON from input arguments.
        """
        try:
            base64_arg = sys.argv[1]
            decoded_data = base64.b64decode(base64_arg)
            self._data = json.loads(decoded_data)
        except base64.binascii.Error as e:
            raise base64.binascii.Error(f"Error while decoding base64 data from input arguments, error: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error while decoding JSON from input arguments, error: {e}", e.doc, e.pos)
        except Exception as e:
            raise Exception(f"Error while loading data from input arguments, error: {e}")

    def _load_data_from_file(self):      
        """
        Load data from a file and parse it as JSON.
        Raises:
            FileNotFoundError: If the input file is not found.
            json.JSONDecodeError: If there is an error while decoding JSON from the input file.
            Exception: If there is an error while loading data from the input file.
        """
        try:
            file_path = os.path.join(os.getcwd(), INPUT_FILE_NAME)
            with open(file_path, "r") as f:
                self._data = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Input file {file_path} not found, error: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error while decoding JSON from input file {file_path}, error: {e}", e.doc, e.pos)
        except Exception as e:
            raise Exception(f"Error while loading data from input file {file_path}, error: {e}")

    def get_value(self, key):
        """
        Get the value associated with the given key from the loaded data.
        Args:
            key (str): The key to retrieve the value for.
        Returns:
            The value associated with the given key, or None if the key is not found.
        """
        return self._data.get(key)

    def get_open_api_url(self):
        """
        Get the Open API URL from the loaded data.
        Returns:
            str: The Open API URL.
        """
        return self.get_value("cwOpenAPIURL")
