# pyotp-mgr
Leif Gregory <leif@devtek.org>
totp.py v1.0
Tested to Python v3.7.3

Description:
Generate and display QR codes for TOTP while also saving them in encrypted
format to a file (default) or DB (optional). This application acts as a TOTP
key manager similar to a password manager such as KeePass etc.

Functions provided:
- Generate TOTP Secret Key
- Generate a QR code URI
- Generate a QR code using the URI
- Generate a Fernet encryption key for first time users
- Optionally provide the Fernet Key as --key option, fernet.key file, or OS environment variable FERNETKEY
- Save the TOTP record to a file as encrypted strings (default function)
- Optionally save TOTP record to a SQLite DB instead the file as encrypted strings (--DB option)
- Optionally save QR code to a .jpg output file (-o option)
- Optionally display all stored TOTP records from a file or DB decrypted to the screen (--decrypt option)
- Optionally generate and display a QR code for each TOTP record (--rebuild flag)
- Optionally generate a looped test for validating an authenticator app TOTP code (-t flag)
- Optionally display verbose output to copy and paste TOTP secretKey and TOTP URI (--verbose option)

- Fernet Information: https://cryptography.io/en/latest/Fernet/

Changelog:
20190820 -  Added ability to set FERNETKEY as an OS environment variable.
20190818 -  Added --rebuild feature and Fernet key generation as a file or with
            --key option, added DB functions for TOTP storage.
20190816 -  Initial code
