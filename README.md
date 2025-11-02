# Mini Password Manager

[![Release](https://img.shields.io/github/v/release/amir-codes-here/password-manager?label=release)](https://github.com/amir-codes-here/password-manager/releases)
[![License](https://img.shields.io/github/license/amir-codes-here/password-manager)](https://github.com/amir-codes-here/password-manager/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/amir-codes-here/password-manager)](https://github.com/amir-codes-here/password-manager/issues)

A secure, minimal, and user-friendly password manager intended for personal or small-team use. This repository contains the code, documentation, and tests for storing, encrypting, and retrieving credentials safely.

### Table of Contents
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Usage](#usage)
- [Data Backup & Recovery](#data-backup--recovery)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

## Key Features
- Strong encryption of stored secrets (recommendations and configuration examples included).
- Zero-knowledge or passphrase-based encryption model (adapt to your use-case).
- Export/Import of encrypted vaults.
- CLI for quick access and workflows (or a simple GUI/web UI if provided).
- Extensible storage backends (file, SQLite, cloud providers).
- Audit logging and optional secure clipboard handling.

## Getting Started

### Prerequisites
- Git
- The language runtime / package manager for this project (update the list below to match the repo):
  - Node.js (>=14) and npm/yarn, or
  - Python (>=3.8) and pip, or
  - Go (>=1.18)
- (Optional) A hardware-backed key (e.g., YubiKey) or OS keyring for additional security.

### Installation
Clone the repo:
```bash
git clone https://github.com/amir-codes-here/password-manager.git
cd password-manager
```

Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Quick Start
simply run the python code in your terminal

```bash
python run.py
```

## Usage

- In order to **save new passwords** to vault, visit the "Add" tab
- In order to **view saved passwords** or **delete** one, visit the "View" tab
- In order to **update an existing password**, visit the "Update" tab
- In order to **change app's password**, visit the "Settings" tab
- You can access a minimal and safe **password generation tool** in the "Tools" tab 

## Data Backup & Recovery
- There is a backup vault and backup of the encryption key in this directory :
  - For windows : Your `%TEMP%` folder
  - For macOS : Probably `/var/folders/<random>/T` or `/tmp`
  - For linux : Your `$TMPDIR` if set. otherwise probably `/tmp`
- You can find the vault's backup file name and the encryption key's backup file name in `_backend.py` (`BACKUP_VAULT_FILE_NAME` and `BACKUP_KEY_FILE_NAME`)
- The app will automatically recover lost data from the relative backup files, but it is recommended to have a copy of them somewhere safe.

## Security Notes
- The app's password is encrypted and saved inside your OS credential manager via `keyring`. if by any chance that password is deleted, for security purposes, the app automatically deletes the vault, the encryption key and all backups completely and **all saved data will be lost forever!**

## Contributing
Sadly, this is a personal, minimal project and contributions are not welcome.

## Contact
Maintainer: amir-codes-here

For feature requests, bug reports, and general discussion, please open an issue in the repository.

## Acknowledgements
Thanks to the open-source crypto and password-manager communities for prior art and guidance.

