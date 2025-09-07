import os
import platform
import subprocess
import tempfile
import keyring
import base64
import secrets
import string
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
import json


# ---------------- setup --------------------
KEY_FILE_NAME = '.key'
VAULT_FILE_NAME = 'vault.json'
BACKUP_KEY_FILE_NAME = 'key.bin'
BACKUP_VAULT_FILE_NAME = 'vault-bu.json'
KEYRING_SERVICE_NAME = 'PasswordManagerPy'
KEYRING_USERNAME = 'password-manager-py'
HASH_SALT_LENGTH = 20
KEK_FALLBACK = 'uT7.)Jkn826-2+jDd'


# ----------------- directory & file related functions -----------------
def get_key_directory() -> Path:
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        return Path(os.getenv("LOCALAPPDATA")).resolve()
    elif system == "Darwin":  # macOS
        return (home / "Library" / "Caches").resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("XDG_DATA_HOME", home / ".local" / "share")).resolve()

def get_vault_directory() -> Path:
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        return Path(os.getenv("APPDATA")).resolve()
    elif system == "Darwin":  # macOS
        return (home / "Library" / "Application Support").resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("XDG_CONFIG_HOME", home / ".config")).resolve()

def get_backup_directory() -> Path:
    system = platform.system()

    if system == "Windows":
        return Path(os.getenv("TEMP", tempfile.gettempdir())).resolve()
    elif system == "Darwin":  # macOS
        return Path(tempfile.gettempdir()).resolve()
    else:  # Linux & other Unix
        return Path(os.getenv("TMPDIR", tempfile.gettempdir())).resolve()
    
def generate_key_file() -> None:
    d = get_key_directory()
    file_path = d / KEY_FILE_NAME

    if os.path.isfile(file_path):
        return
    
    backup_path = get_backup_directory() / BACKUP_KEY_FILE_NAME

    if os.path.isfile(backup_path):
        key = get_backup_key()

    else:
        key = generate_enc_key()
        kek = get_KEK()
        key = encrypt_text(key.decode(), kek)

    with open(file_path, 'wb') as file:
        file.write(key)

    # Restrict permissions on Linux/macOS . owner read/write only
    if platform.system() != 'Windows':
        try:
            os.chmod(file_path, 0o600)
        except Exception:
            pass

def generate_vault_file() -> None:
    d = get_vault_directory()
    file_path = d / VAULT_FILE_NAME

    if os.path.isfile(file_path):
        return
    
    backup_file = get_backup_directory() / BACKUP_VAULT_FILE_NAME

    if os.path.isfile(backup_file):
        data = get_backup_vault_data()
        with open(file_path, 'w') as f:
            json.dump(data, f)

    else:
        with open(file_path, 'w') as f:
            pass

def write_data_to_vault(data: dict[str: str], encript_data: bool = True) -> None:
    d = get_vault_directory()
    file_path = d / VAULT_FILE_NAME
    data = encrypt_dict(data) if encript_data else data
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=3)

def read_data_from_vault(decrypt_data: bool = True) -> dict | None:
    d = get_vault_directory()
    file_path = d / VAULT_FILE_NAME

    if not os.path.isfile(file_path):
        return None
    
    with open(file_path, 'r') as f:
        data = json.load(f)

    return decrypt_dict(data) if decrypt_data else data

def update_backup_files() -> None:
    backup_dir = get_backup_directory()
    key_file_path = get_key_directory() / KEY_FILE_NAME
    vault_file_path = get_vault_directory() / VAULT_FILE_NAME
    backup_key_file_path = backup_dir / BACKUP_KEY_FILE_NAME
    backup_vault_file_path = backup_dir / BACKUP_VAULT_FILE_NAME

    if os.path.isfile(key_file_path):
        with open(key_file_path, 'rb') as f:
            key = f.readline()

        with open(backup_key_file_path, 'wb') as f:
            f.write(key)
    
    if os.path.isfile(vault_file_path):
        with open(vault_file_path, 'r') as f:
            key = f.readline()

        with open(backup_vault_file_path, 'w') as f:
            f.write(key)

def get_backup_key(decrypt_key: bool = False) -> bytes:
    file_path = get_backup_directory() / BACKUP_KEY_FILE_NAME

    with open(file_path, 'rb') as f:
        data = f.readline()

    if decrypt_dict:
        kek = get_KEK()
        data = decrypt_text(data.decode(), kek)

    return data

def get_backup_vault_data(decrypt_data: bool = False) -> dict[str: str]:
    file_path = get_backup_directory() / BACKUP_VAULT_FILE_NAME
    with open(file_path, 'r') as f:
        data = json.load(f)
    return decrypt_dict(data) if decrypt_data else data


# ----------------- cryptography related functions -----------------------
def get_motherboard_serial() -> str:
    system = platform.system()

    if system == "Windows":
        try:
            output = subprocess.check_output(
                ["wmic", "baseboard", "get", "serialnumber"],
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            ).decode(errors="ignore").splitlines()
            serial = [line.strip() for line in output if line.strip() and "SerialNumber" not in line]
            if serial:
                return serial[0]
        except Exception:
            pass

    elif system == "Linux":
        try:
            path = "/sys/class/dmi/id/board_serial"
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        try:
            output = subprocess.check_output(
                ["dmidecode", "-s", "baseboard-serial-number"],
                stderr=subprocess.DEVNULL
            )
            return output.decode(errors="ignore").strip()
        except Exception:
            pass

    elif system == "Darwin":  # macOS
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"],
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            for line in output.splitlines():
                if "Serial Number" in line:
                    return line.split(":")[1].strip()
        except Exception:
            pass

    return KEK_FALLBACK

def turn_text_to_enc_key(text: str) -> bytes:
    digest = hashlib.sha256(text.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def get_KEK() -> bytes:  # KEK := Key Encryption Key
    data = get_motherboard_serial() * 2
    kek = turn_text_to_enc_key(data)
    return kek

def generate_enc_key() -> bytes:
    return Fernet.generate_key()

def get_enc_key() -> bytes:
    file_path = get_key_directory() / KEY_FILE_NAME
    with open(file_path, 'rb') as f:
        key = f.readline()
    kek = get_KEK()
    key = decrypt_text(key.decode(), kek)
    return key

def encrypt_text(text: str, key: bytes = None) -> bytes:
    key = get_enc_key() if key is None else key
    cipher = Fernet(key)
    enc_text = cipher.encrypt(text.encode())
    return enc_text

def decrypt_text(text: str, key: bytes = None) -> bytes:
    key = get_enc_key() if key is None else key
    cipher = Fernet(key)
    dec_text = cipher.decrypt(text.encode())
    return dec_text

def encrypt_dict(data: dict[str: str]) -> dict[str: str]:
    enc_data = {}
    key = get_enc_key()
    cipher = Fernet(key)

    for key, value in data.items():
        enc_key = cipher.encrypt(key.encode()).decode()
        enc_value = cipher.encrypt(value.encode()).decode()
        enc_data[enc_key] = enc_value

    return enc_data


def decrypt_dict(data: dict[str: str]) -> dict[str: str]:
    dec_data = {}
    key = get_enc_key()
    cipher = Fernet(key)

    for key, value in data.items():
        dec_key = cipher.decrypt(key.encode()).decode()
        dec_value = cipher.decrypt(value.encode()).decode()
        dec_data[dec_key] = dec_value

    return dec_data


# --------------- system credential manager related functions -------------
def app_pass_exists() -> bool:
    data = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    return bool(data)

def generate_salt() -> str:
    salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(HASH_SALT_LENGTH))
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

def set_new_app_pass(password: str) -> bool:
    if password:
        # todo: validate the password first
        salt, hashed_pass = hash_password(password, gen_salt=True)

        if app_pass_exists():
            keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)

        data = salt + hashed_pass
        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, data)
        
        return True
    return False

def app_pass_is_valid(password: str) -> bool:
    return len(password) >= 8

def app_pass_is_correct(password: str) -> bool:
    app_pass = get_hashed_pass_from_keyring()
    _, hashed_pass = hash_password(password)
    return hashed_pass == app_pass


# --------------- data minipulation functions -------------
def reset_all() -> None:
    files = [
        get_key_directory() / KEY_FILE_NAME,
        get_vault_directory() / VAULT_FILE_NAME,
        get_backup_directory() / BACKUP_KEY_FILE_NAME,
        get_backup_directory() / BACKUP_VAULT_FILE_NAME,
    ]

    for file in files:
        if os.path.exists(file):
            os.remove(file)

    if app_pass_exists():
        keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
