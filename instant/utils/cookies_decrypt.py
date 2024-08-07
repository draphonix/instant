#!/usr/bin/env python3

# Usage:
# $ ./chrome_cookies_decrypt.py > cookie.txt

import os
import sqlite3
import keyring
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class ChromeCookiesDecrypt:
    def __init__(self):
        self.passwd = keyring.get_password(os.getenv('BROWSER_STORAGE'), os.getenv('BROWSER_NAME'))
        self.passwd = self.passwd.encode()
        self.salt = b'saltysalt'
        self.length = 16
        self.iterations = 1003
        self.key = PBKDF2(self.passwd, self.salt, self.length, self.iterations)
        self.cipher = AESCipher(self.key)
        self.cookie_file = os.path.expanduser(os.getenv('COOKIE_FILE_PATH'))
        self.conn = sqlite3.connect(self.cookie_file)
        self.sql = "SELECT host_key,path,is_secure,name,value,encrypted_value,((expires_utc/1000000)-11644473600) FROM cookies WHERE host_key LIKE '%jira.scopely.io%'"

    def get_cookie_str(self):
        cookie_str = ''
        rows = list(self.conn.execute(self.sql))
        for i, (host_key, path, is_secure, name, _value, encrypted_value, _exptime) in enumerate(rows):
            value = _value
            if encrypted_value[:3] == b'v10':
                encrypted_value = encrypted_value[3:]  # Trim prefix 'v10'
                value = self.cipher.decrypt(encrypted_value)
                value = value.decode()
            cookie_str = cookie_str + name + '=' + value
            if i < len(rows) - 1:
                cookie_str = cookie_str + ';'


        self.conn.rollback()
        return cookie_str

class AESCipher:
    def __init__(self, key):
        self.key = key

    def decrypt(self, text):
        cipher = AES.new(self.key, AES.MODE_CBC, IV=(' ' * 16))
        return self._unpad(cipher.decrypt(text))

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

if __name__ == '__main__':
    decryptor = ChromeCookiesDecrypt()
    cookie_str = decryptor.get_cookie_str()
    print(cookie_str)



