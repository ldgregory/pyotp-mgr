# pyotp-mgr v1.0

## Description:
Generate and display QR codes for TOTP while also saving them in encrypted format to a file (default) or DB (optional). This application acts as a TOTP key manager similar to a password manager such as KeePass etc. The rebuild function will generate QR codes for every stored TOTP code allowing you to quickly scan them one after the other with your mobile TOTP app.

## Functions provided:
- Generate TOTP Secret Key
- Generate a QR code URI
- Generate a QR code using the URI
- Generate a Fernet encryption key for first time users
- Optionally provide the Fernet Key as --key option, fernet.key file, or OS environment variable FERNETKEY
- Optionaly enter a TOTP key in manually in cases where the key was generated somewhere else (-m option)
- Save the TOTP record to a file as encrypted strings (default function)
- Optionally save TOTP record to a SQLite DB instead of the file as encrypted strings (--db option)
- Optionally save QR code to a .jpg output file (-o option)
- Optionally display all stored TOTP records decrypted to the screen (--decrypt option)
- Optionally generate and display a QR code for each TOTP record (--rebuild flag)
- Optionally generate a looped test for validating an authenticator app TOTP code (-t flag)
- Optionally display verbose output to copy and paste generated TOTP secretKey and TOTP URI (--verbose option)

- Fernet Information: https://cryptography.io/en/latest/Fernet/

## Changelog:
- 20190820 -  Added ability to set FERNETKEY as an OS environment variable.
- 20190818 -  Added --rebuild feature and Fernet key generation as a file or with --key option, added DB functions for TOTP storage.
- 20190816 -  Initial code

## Usage:
The first time you use the application, it will ask you to generate a Fernet key. This key can be copied and pasted and stored securely in your choice of location and you'll be required to use the --key option. Alternatively, it can save it to the file fernet.key in the same directory as the application and will automatically use it in the future. A third alternative is to set an OS environment variable called FERNETKEY (in Linux, edit your ~/.profile and create a line at the end `export FERNETKEY=<key>` replacing <key> with your actual key.)

Below examples assume I have a fernet.key file or set it as a FERNETKEY OS environment variable. We'll also assume the TOTP key is for a website called "DevTek.org" with a user account of "leif.gregory"

###### Generate a TOTP QR code and store details in encrypted format in totp.txt (default behaviour)
**python3 pyotp-mgr -a leif.gregory -i DevTek.org**

###### Generate a TOTP QR code and store details in encrypted format in a SQLite DB instead of totp.txt
**python3 pyotp-mgr -a leif.gregory -i DevTek.org --db**

###### Generate a TOTP QR code and store details for a TOTP code that was generated elsewhere (TOTP key management feature)
**python3 pyotp-mgr -a leif.gregory -i DevTek.org -m**

- If you want to see the TOTP key and the QR Code URI, just add `--verbose` to any of the above.
- If you'd like to save the generated QR code to a file for safekeeping, use the `-o <filename>` option with any of the above.
- If you'd like to test your newly generated or manually entered TOTP code, you can use the `-t` flag to run a looped test.

###### Display all stored TOTP codes in decrypted format from totp.txt (default behaviour)
**python3 pyotp-mgr --decrypt**

###### Display all stored TOTP codes in decrypted format from the SQLite DB
**python3 pyotp-mgr --decrypt --db**

The rebuild feature allows you to generate QR Codes to display on screen for all stored TOTP codes. This is useful if you've lost your mobile device or something else happened where your mobile TOTP app became unusable.

###### Disaply a QR code for all stored TOTP codes from totp.txt
**python3 pyotp-mgr --rebuild**

###### Disaply a QR code for all stored TOTP codes from the SQLite DB
**python3 pyotp-mgr --rebuild --db**
