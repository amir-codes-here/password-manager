import os
import platform
import tempfile
import keyring
import base64
import secrets
import string
import hashlib
from pathlib import Path


KEY_FILE_NAME = '.key'
VAULT_FILE_NAME = 'vault.json'
BACKUP_KEY_FILE_NAME = 'key.bin'
BACKUP_VAULT_FILE_NAME = 'vault-bu.json'
KEYRING_SERVICE_NAME = 'PasswordManagerPy'
KEYRING_USERNAME = 'password-manager-py'
HASH_SALT_LENGTH = 20


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
    # todo: change later
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



def app_pass_exists() -> bool:
    data = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    return bool(data)

def generate_salt() -> str:
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(HASH_SALT_LENGTH))
    print(f"new salt generetaed :\n{salt}")
    return salt

def get_salt_from_keyring() -> str:
    salt = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)[:HASH_SALT_LENGTH]
    return salt

def get_hashed_pass_from_keyring() -> str:
    hashed_pass = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)[HASH_SALT_LENGTH:]
    return hashed_pass

def hash_password(password: str, gen_salt: bool = False) -> tuple[str]:
    salt = generate_salt() if gen_salt else get_salt_from_keyring()

    hashed_pass = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode(), 
        salt.encode(), 
        100_000
    )

    return (salt, hashed_pass.hex())


def _save_app_pass_to_system(password: str, salt: str) -> bool:
    '''
    entered password must be hashed
    '''
    if password and salt:
        if app_pass_exists():
            keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        data = salt + password
        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, data)
        return True
    return False


def set_new_app_pass(password: str):
    # todo: validate the password first
    salt, hashed_pass = hash_password(password, gen_salt=True)
    _save_app_pass_to_system(hashed_pass, salt)


def validate_app_password(password: str) -> bool:
    app_pass = get_hashed_pass_from_keyring()
    _, hashed_pass = hash_password(password)
    return hashed_pass == app_pass
