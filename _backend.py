import os
import platform
import tempfile
import keyring
import base64
import hashlib
from pathlib import Path


KEY_FILE_NAME = '.key'
VAULT_FILE_NAME = 'vault.json'
BACKUP_KEY_FILE_NAME = 'key.bin'
BACKUP_VAULT_FILE_NAME = 'vault-bu.json'
KEYRING_SERVICE_NAME = 'PasswordManagerPy'
KEYRING_USERNAME = 'password-manager-py'


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


def generate_enc_key():
    #  todo: change later
    return 'iurfhnslkhnsrtghdknrsekg'


def generate_key_file():
    d = get_key_directory()
    file_path = d / KEY_FILE_NAME
    if os.path.isfile(file_path):
        return
    key = generate_enc_key()
    with open(file_path, 'wb') as file:
        file.write(key)

    # Restrict permissions on Linux/macOS . owner read/write only
    if platform.system() != 'Windows':
        try:
            os.chmod(file_path, 0o600)
        except Exception:
            pass


def check_if_app_pass_exists():
    data = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    return bool(data)
