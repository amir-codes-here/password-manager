import os
import platform
import tempfile
from pathlib import Path

def get_key_directory():
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        return Path(os.getenv("LOCALAPPDATA")).resolve()
    elif system == "Darwin":  # macOS
        return (home / "Library" / "Caches").resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("XDG_DATA_HOME", home / ".local" / "share")).resolve()

def get_vault_directory():
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        return Path(os.getenv("APPDATA")).resolve()
    elif system == "Darwin":  # macOS
        return (home / "Library" / "Application Support").resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("XDG_CONFIG_HOME", home / ".config")).resolve()

def get_temp_directory():
    system = platform.system()

    if system == "Windows":
        return Path(os.getenv("TEMP", tempfile.gettempdir())).resolve()
    elif system == "Darwin":  # macOS
        return Path(tempfile.gettempdir()).resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("TMPDIR", tempfile.gettempdir())).resolve()


# # Example usage
# print("Key directory:   ", get_key_directory())
# print("Vault directory: ", get_vault_directory())
# print("Temp directory:  ", get_temp_directory())
