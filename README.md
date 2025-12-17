# Password Manager (Tkinter, Python)

A secure, cross-platform desktop password manager written in **Python 3.12** using **Tkinter** for the GUI and **Fernet (cryptography)** for encryption. The application securely stores credentials in an encrypted local vault, protects access with a master password, and maintains automatic backup files for recovery.

---

## Features

* **Encrypted password vault** using Fernet symmetric encryption
* **Master password protection** (hashed and stored securely via OS keyring)
* **Automatic backup & recovery** of vault and encryption key
* **Cross-platform support** (Windows, macOS, Linux)
* **Search, add, update, delete** stored passwords
* **Strong password generator** with configurable length
* **Clipboard copy support**
* **Automatic logout after inactivity**
* **Graceful shutdown handling** (updates backups on app close)

---

## Screens / Application Tabs

* **Login / Set Password** – Secure entry point
* **View** – Browse and copy saved passwords
* **Add** – Store new credentials
* **Update** – Modify existing entries
* **Tools** – Strong password generator
* **Settings** – Change master password

---

## Project Structure

```text
.
├── run.py                 # Main Tkinter application
├── _backend.py            # Encryption, storage, backup, and security logic
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

---

## Security Design

### Vault Encryption

* All stored credentials are encrypted using **Fernet (AES + HMAC)**
* Both keys and values are encrypted
* Vault stored as encrypted JSON (`vault.json`)

### Key Management

* A randomly generated encryption key is stored encrypted on disk
* The encryption key itself is protected using a **Key Encryption Key (KEK)**
* The KEK is derived from hardware-specific identifiers (with a fallback)

### Master Password

* Never stored in plaintext
* Hashed using **PBKDF2-HMAC-SHA256** with salt
* Stored securely via the system keyring

### Backups

* Backup copies are automatically maintained for:

  * Vault file
  * Encryption key
* Backups are restored automatically if primary files are missing
* Backups are updated on **every clean application shutdown**

---

## File Locations (By OS)

### Vault & Key Files

| OS      | Vault Location                  | Key Location       |
| ------- | ------------------------------- | ------------------ |
| Windows | `%APPDATA%`                     | `%LOCALAPPDATA%`   |
| macOS   | `~/Library/Application Support` | `~/Library/Caches` |
| Linux   | `~/.config`                     | `~/.local/share`   |

### Backup Files

Stored in the system temporary directory:

* `vault-bu.json`
* `key.bin`

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/password-manager.git
cd password-manager
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### Required Packages

* `cryptography`
* `keyring`

(Tkinter ships with standard Python distributions.)

---

## Running the Application

```bash
python run.py
```

On first launch:

* You will be prompted to create a **master password**
* The encrypted vault and key files will be initialized automatically

---

## Usage Notes

* **Closing the window** safely updates backup files
* After **5 minutes of inactivity**, the app automatically returns to the login screen
* Deleting the main vault files will trigger **automatic restore from backup** (if available)

---

## Development Notes

### Graceful Shutdown Handling

The application registers a `WM_DELETE_WINDOW` protocol handler to ensure backups are updated whenever the app exits:

```python
root.protocol("WM_DELETE_WINDOW", before_app_close)
```

### JSON Integrity

Vault backups store the full JSON content to avoid corruption during restore.

---

## Limitations

* Single-user local application
* No cloud sync
* Hardware-based KEK may change on some systems (fallback included)

---

## Roadmap / Possible Enhancements

* Vault export/import
* Encrypted cloud synchronization
* Multi-profile support
* Password strength validation
* UI theming (dark mode)

---

## Disclaimer

This project is intended for **educational and personal use**. While strong cryptographic primitives are used, it has **not undergone a formal security audit**. Do not rely on it for high-risk or enterprise-grade password storage without further review.

---

## License

MIT License

---

## Author

Developed by **Amir Jahani**

If you find this project useful, feel free to fork, improve, or submit pull requests.
