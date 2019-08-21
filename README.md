# pyotp-mgr v1.0

Description:
Generate and display QR codes for TOTP while also saving them in encrypted format to a file (default) or DB (optional). This application acts as a TOTP key manager similar to a password manager such as KeePass etc. The rebuild function will generate QR codes for every stored TOTP code allowing you to quickly scan them one after the other with your mobile TOTP app.

Functions provided:
- Generate TOTP Secret Key
- Generate a QR code URI
- Generate a QR code using the URI
- Generate a Fernet encryption key for first time users
- Optionally provide the Fernet Key as --key option, fernet.key file, or OS environment variable FERNETKEY
- Save the TOTP record to a file as encrypted strings (default function)
- Optionally save TOTP record to a SQLite DB instead of the file as encrypted strings (--db option)
- Optionally save QR code to a .jpg output file (-o option)
- Optionally display all stored TOTP records decrypted to the screen (--decrypt option)
- Optionally generate and display a QR code for each TOTP record (--rebuild flag)
- Optionally generate a looped test for validating an authenticator app TOTP code (-t flag)
- Optionally display verbose output to copy and paste generated TOTP secretKey and TOTP URI (--verbose option)

- Fernet Information: https://cryptography.io/en/latest/Fernet/

Changelog:
20190820 -  Added ability to set FERNETKEY as an OS environment variable.
20190818 -  Added --rebuild feature and Fernet key generation as a file or with
            --key option, added DB functions for TOTP storage.
20190816 -  Initial code
