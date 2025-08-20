import os
import platform
import tempfile
import keyring
import base64
import secrets
import string
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet


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

def get_temp_directory() -> Path:
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


# ----------------- cryptography related functions -----------------------
import platform
import subprocess
import os

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

def get_enc_key() -> str:
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


# --------------- system credential manager related functions -------------
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


def set_new_app_pass(password: str) -> bool:
    if password and salt:
        # todo: validate the password first
        salt, hashed_pass = hash_password(password, gen_salt=True)
        if app_pass_exists():
            keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        data = salt + hashed_pass
        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, data)
        return True
    return False


def validate_app_password(password: str) -> bool:
    app_pass = get_hashed_pass_from_keyring()
    _, hashed_pass = hash_password(password)
    return hashed_pass == app_pass

