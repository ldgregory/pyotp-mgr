#! /usr/bin/env python3

"""
Leif Gregory <leif@devtek.org>
totp.py v1.1
Tested to Python v3.7.3

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
20190820 -  Added ability to set FERNETKEY as an OS environment variable.
20190818 -  Added --rebuild feature and Fernet key generation as a file or with
            --key option, added DB functions for TOTP storage.
20190816 -  Initial code

Copyright 2020 Leif Gregory

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import pyotp
import qrcode
from cryptography.fernet import Fernet
from os import path, environ
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


class TextColor:
    BLOGR = str('\033[7;32;40m')
    BLUE = str('\033[1;34;40m')
    GREEN = str('\033[1;32;40m')
    PURPLE = str('\033[1;35;40m')
    RED = str('\033[1;31;40m')
    RESET = str('\033[0m')
    YELLOW = str('\033[1;33;40m')


def dbRead(fernetKey, rebuild=None):
    """
    This is an optional function (--db flag) to read, decrypt and display TOTP
    records from the DB when the --decrypt or --rebuild option is used.
    """

    # Set up the DB (otp.s3db) connection for SQLite
    engine = create_engine('sqlite:///otp.s3db', echo=False)
    metadata = MetaData(engine)
    users = Table('users', metadata, autoload=True)

    s = users.select()
    rs = s.execute()

    for row in rs:
        if rebuild:  # Display a QR code for each TOTP record
            img = qrcode.make(row.otpQRURI)
            img.show()
        else:
            # print(f"\n{TextColor.RED}Account:\t{TextColor.RESET}{row.account}\n{TextColor.RED}OTP Secret Key:\t{TextColor.RESET}{row.secretKey}\n{TextColor.RED}OTP QR URI:\t{TextColor.RESET}{row.otpQRURI}")
            print(f"\n{TextColor.GREEN}Account:\t{TextColor.RESET}{decrypt(row.account, fernetKey).decode()}\n{TextColor.GREEN}OTP Secret Key:\t{TextColor.RESET}{decrypt(row.secretKey, fernetKey).decode()}\n{TextColor.GREEN}OTP QR URI:\t{TextColor.RESET}{decrypt(row.otpQRURI, fernetKey).decode()}")

    return None


def dbWrite(account, secretKey, qrURI, fernetKey):
    """
    This is an optional function (--db flag) to store the generated TOTP
    account, TOTP secretKey and TOTP QR URI to the DB as encrypted strings.
    """

    # Set up the DB (otp.s3db) connection for SQLite
    engine = create_engine('sqlite:///otp.s3db', echo=False)
    metadata = MetaData(engine)

    # Define the table, checkfirst=True will not re-create the table if it
    # already exists.
    users = Table('users', metadata,
        Column('user_id', Integer, primary_key=True),
        Column('account', String),
        Column('secretKey', String),
        Column('otpQRURI', String))
    users.create(checkfirst=True)

    # Insert the new TOTP record as encrypted strings
    i = users.insert()
    i.execute(account=encrypt(account.encode(), fernetKey),
              secretKey=encrypt(secretKey.encode(), fernetKey),
              otpQRURI=encrypt(qrURI.encode(), fernetKey))

    return None


def fileWrite(account, secretKey, qrURI, fernetKey):
    """
    This is the default function of the application to write TOTP records to
    totp.txt as an encrypted string. This function will not be used if the --db
    flag is used.
    """
    with open('totp.txt', 'a') as f:
        temp = account + ',' + secretKey + ',' + qrURI
        encData = encrypt(temp.encode(), fernetKey).decode() + '\n'
        f.write(encData)

    return None


def fileRead(fernetKey, rebuild=None):
    """
    This is a default function of the application to read, decrypt and display
    TOTP records from totp.txt and decrypt them. This function will not be used
    if the --db flag is used. It will either display each TOTP record, or
    generate QR codes for each record with the --rebuild flag.
    """

    with open('totp.txt', 'r') as f:
        for line in f:
            plainText = decrypt(line.encode(), fernetKey).decode()
            x = plainText.split(',')
            if rebuild:  # Display a QR code for each TOTP record
                img = qrcode.make(x[2])
                img.show()
            else:
                print(f"\n{TextColor.GREEN}Account:\t{TextColor.RESET}{x[0]}\n \
                      {TextColor.GREEN}OTP Secret Key:\t{TextColor.RESET}{x[1]}\n \
                      {TextColor.GREEN}OTP QR URI:\t{TextColor.RESET}{x[2]}")

    return None


def decrypt(token: bytes, key: bytes) -> bytes:
    """
    Decrypts Fernet encrypted TOTP records
    """

    return Fernet(key).decrypt(token)


def encrypt(message: bytes, key: bytes) -> bytes:
    """
    Encrypts TOTP records using Fernet
    """

    return Fernet(key).encrypt(message)


def main():
    parser = argparse.ArgumentParser(description='TOTP Generator')
    parser.add_argument('-o', type=str, help='Filename to save QR code to', dest='totpOutFile')
    parser.add_argument('-m', type=str, help='Manually enter a TOTP shared secret key', dest='totpManual')
    parser.add_argument('-a', type=str, help='Account: User account TOTP is for', dest='totpAccount')
    parser.add_argument('-i', type=str, help='Issuer: Application or site TOTP is for', dest='totpIssuer')
    parser.add_argument('-t', help='Test codes after generation', action='store_true', dest='totpTest')
    parser.add_argument('--db', help='Store or read TOTPs from DB instead of file', action='store_true', dest='totpDB')
    parser.add_argument('--decrypt', help='Display all stored TOTP codes', action='store_true', dest='totpDecrypt')
    parser.add_argument('--key', type=str, help='Fernet encryption / decryption Key', dest='totpFernetKey')
    parser.add_argument('--rebuild', help='Display all stored codes as QR codes to rebuild TOTP app', action='store_true', dest='totpRebuild')
    parser.add_argument('--verbose', help='Show all output', action='store_true', dest='totpVerbose')
    parser.add_argument('-v', action='version', version='%(prog)s 1.0', dest='version')
    args = parser.parse_args()

    # First let's check if we have an encryption key. If they don't have one,
    # let's generate one for them for future use.
    if args.totpFernetKey or environ.get('FERNETKEY') or path.exists("./fernet.key"):
        if args.totpFernetKey:
            fernetKey = args.totpFernetKey
        elif environ.get('FERNETKEY'):
            fernetKey = environ.get('FERNETKEY')
        elif path.exists('./fernet.key'):
            with open('./fernet.key', 'r') as f:
                fernetKey = f.readline()

        # Check if they just want to decrypt (--decrypt flag) TOTP records in
        # or they want to Rebuild (--rebuild flag). Rebuild will generate a QR
        # code for each stored TOTP record.
        if args.totpDecrypt or args.totpRebuild:
            if args.totpDB:
                dbRead(fernetKey, args.totpRebuild)
            else:
                fileRead(fernetKey, args.totpRebuild)

        # Everything here is for the generation, saving and displaying of TOTP
        # codes.
        else:
            account = input('Account: ') if args.totpAccount is None else args.totpAccount
            issuer = input('Issuer: ') if args.totpIssuer is None else args.totpIssuer

            # Generate or get the shared secret key (-m option) and generate the QR URI
            secretKey = args.totpManual if args.totpManual else pyotp.random_base32()
            qrURI = pyotp.totp.TOTP(secretKey).provisioning_uri(account, issuer_name=issuer)

            # Create a qrcode image for the pyotp generated URI and display it
            # otpauth://totp/<issuer>:<account>?secret=<secretKey>&issuer=<issuer>
            img = qrcode.make(qrURI)
            img.show()

            # Show details used to generate QR code (--verbose flag)
            if args.totpVerbose:
                print(f"Shared secret key:\t{TextColor.YELLOW}{secretKey}{TextColor.RESET}")
                print(f"QR Code URI:\t\t{TextColor.YELLOW}{qrURI}{TextColor.RESET}")

            # Save the TOTP QR code to an image file for backup purposes (-o flag)
            if args.totpOutFile:
                outFile = args.totpOutFile if args.totpOutFile[-4:].lower() == '.jpg' else args.totpOutFile + '.jpg'

                # Handle if a file with that name already exists in the current folder
                if path.exists(outFile):
                    import datetime
                    newFilename = outFile[0:-4] + '_' + str(datetime.datetime.now().time()) + '.jpg'
                    img.save(newFilename)
                    print(f"{TextColor.RED}Filename {outFile} already exists, saved to {newFilename}")
                else:
                    img.save(outFile)

                # Show detail (--verbose flag)
                if args.totpVerbose:
                    print(f"Backup saved to:\t{TextColor.YELLOW}{outFile}{TextColor.RESET}")

            if args.totpDB:
                # Write the TOTP to a DB (--db flag)
                dbWrite(account, secretKey, qrURI, fernetKey)
            else:
                # Write the TOTP to a file (default unless --db is supplied)
                fileWrite(account, secretKey, qrURI, fernetKey)

            if args.totpTest:
                # Give the user the opportunity to test the generated codes are
                # valid. There's about a two second grace period that the
                # previous code will be accepted after it changes on the mobile
                # device. (-t flag)
                totp = pyotp.TOTP(secretKey)
                print(f"\n{TextColor.BLOGR}Test Generated Codes Below. Type exit to quit.{TextColor.RESET}")

                while True:
                    test = input('Input Code to Test: ')
                    if test == 'exit':
                        break
                    else:
                        print(f"{TextColor.GREEN}Successful!{TextColor.RESET}") if totp.now() == test else print(f"{TextColor.RED}Failure!{TextColor.RESET}")

    # Handle first time users who don't have a Fernet encryption / decreption key
    else:
        question = input(f"You don't have a fernet.key file or FERNET environment variable and didn't supply a Fernet\nencryption key with the --key option. Would you like to generate a Fernet key? ")
        if question.lower() == 'y':
            question2 = input(f"\nWould you like your key saved to a file and automatically loaded when this application\nis run, or printed out so you can put it somewhere safer and supply it with the\n--key option or as a FERNET environment variable (file | print)? ")
            if question2.lower() == 'print':
                print(f"\nKeep this key in a safe place, you'll need to supply it with the --key option or\nset it as an environment variable called FERNETKEY:\n{TextColor.BLOGR}{Fernet.generate_key().decode()}{TextColor.RESET}")
            elif question2.lower() == 'file':
                with open('fernet.key', 'w') as f:
                    key = Fernet.generate_key().decode()
                    f.write(key)
                    print(f"Your key {TextColor.BLOGR}{key}{TextColor.RESET} was saved as ./fernet.key. It will be automatically used in the future.")
            else:
                print('\nSorry, not a valid response.')
        else:
            print('\nPlease supply your Fernet key using the --key option, set it as an environment\nvariable called FERNETKEY, or store it in a file called ./fernet.key for automatic use.')


if __name__ == '__main__':
    main()
