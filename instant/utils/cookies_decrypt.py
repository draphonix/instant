#!/usr/bin/env python3

# Usage:
# $ ./chrome_cookies_decrypt.py > cookie.txt

import os
import sqlite3
import keyring
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class ChromeCookiesDecrypt:
    def __init__(self):
        """
        Initialize the ChromeCookiesDecrypt class.
        """
        self.passwd: bytes = self._get_password()
        self.salt: bytes = b'saltysalt'
        self.length: int = 16
        self.iterations: int = 1003
        self.key: bytes = PBKDF2(self.passwd, self.salt, self.length, self.iterations)
        self.cipher: AESCipher = AESCipher(self.key)
        self.cookie_file: str = os.path.expanduser(os.getenv('COOKIE_FILE_PATH', ''))
        self.conn: sqlite3.Connection = sqlite3.connect(self.cookie_file)
        self.sql: str = "SELECT host_key,path,is_secure,name,value,encrypted_value,((expires_utc/1000000)-11644473600) FROM cookies WHERE host_key LIKE '%jira.scopely.io%'"

    def _get_password(self) -> bytes:
        """
        Retrieve the password from the keyring.

        Returns:
            bytes: The password as bytes.
        """
        browser_storage = os.getenv('BROWSER_STORAGE')
        browser_name = os.getenv('BROWSER_NAME')
        if not browser_storage or not browser_name:
            raise ValueError("BROWSER_STORAGE and BROWSER_NAME environment variables must be set")
        passwd = keyring.get_password(browser_storage, browser_name)
        if not passwd:
            raise ValueError(f"No password found for {browser_name} in {browser_storage}")
        return passwd.encode()

    def get_cookie_str(self) -> str:
        """
        Retrieve and decrypt cookies from the SQLite database.

        Returns:
            str: A string of decrypted cookies.
        """
        cookie_str = ''
        try:
            rows = list(self.conn.execute(self.sql))
            for i, (host_key, path, is_secure, name, _value, encrypted_value, _exptime) in enumerate(rows):
                value = _value
                if encrypted_value[:3] == b'v10':
                    encrypted_value = encrypted_value[3:]  # Trim prefix 'v10'
                    value = self.cipher.decrypt(encrypted_value)
                    value = value.decode()
                cookie_str += f"{name}={value}"
                if i < len(rows) - 1:
                    cookie_str += ';'
        except sqlite3.Error as e:
            print(f"An error occurred while accessing the database: {e}")
        finally:
            self.conn.rollback()
        return cookie_str

class AESCipher:
    def __init__(self, key):
        self.key = key

    def decrypt(self, text):
        # Convert the IV to bytes
        iv = b' ' * 16
        cipher = AES.new(self.key, AES.MODE_CBC, IV=iv)
        return self._unpad(cipher.decrypt(text))

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]