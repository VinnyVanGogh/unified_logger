import os
import configparser
import toml
from pathlib import Path

PACKAGE_NAME = "my_package"

def find_package_name():
    package_name = PACKAGE_NAME
    cwd = Path.cwd()
    setup_cfg = cwd / 'setup.cfg'
    pyproject_toml = cwd / 'pyproject.toml'
    
    print(f"Current working directory: {cwd}")
    print(f"Looking for config files in: {cwd}")
    print(f"Setup.cfg path: {setup_cfg}")
    print(f"pyproject.toml path: {pyproject_toml}")
    
    if os.path.exists(setup_cfg):
        print(f"Found setup.cfg at {setup_cfg}")
        config = configparser.ConfigParser()
        config.read(setup_cfg)
        if 'metadata' in config and 'name' in config['metadata']:
            package_name = config['metadata']['name']
            print(f"Found package name in setup.cfg: {package_name}")
    else:
        print("setup.cfg not found")
    
    if os.path.exists(pyproject_toml):
        print(f"Found pyproject.toml at {pyproject_toml}")
        try:
            with open(pyproject_toml, 'r') as file:
                pyproject_data = toml.load(file)
                if project_name := pyproject_data.get('project', {}).get('name'):
                    package_name = project_name
                    print(f"Found package name in pyproject.toml: {package_name}")
                else:
                    print("No project.name found in pyproject.toml")
        except FileNotFoundError:
            print(f"Error: Could not open pyproject.toml at {pyproject_toml}")
        except toml.TomlDecodeError as e:
            print(f"Error parsing pyproject.toml: {e}")
    else:
        print("pyproject.toml not found")

    print(f"Final package name: {package_name}")
    return package_name

def get_pyproject_toml_version():
    try:
        pyproject_path = Path.cwd() / 'pyproject.toml'
        print(f"Attempting to read version from: {pyproject_path}")
        
        if not pyproject_path.exists():
            print(f"Error: pyproject.toml not found at {pyproject_path}")
            return None
            
        with open(pyproject_path, 'r') as file:
            content = file.read()
            print(f"pyproject.toml content:\n{content}")
            pyproject_data = toml.load(pyproject_path)
            version = pyproject_data.get('project', {}).get('version')
            print(f"Found version in pyproject.toml: {version}")
            return version
    except FileNotFoundError:
        print(f"Error: Could not open pyproject.toml at {pyproject_path}")
        return None
    except toml.TomlDecodeError as e:
        print(f"Error parsing pyproject.toml: {e}")
        return None

# Rest of the code remains the same...
