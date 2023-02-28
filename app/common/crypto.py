import os
from binascii import unhexlify

import base58
from Crypto.Cipher import AES


class Crypto:

    def __init__(self):
        hex_key = os.environ.get('AES_HEX_KEY', '2545bd8abea8bcdbb0b53f1af7897cea4eff5bd5182e902bac9eef4c50e3377a')
        self.key = unhexlify(hex_key)

    def encrypt(self, data, encode=True):
        cipher = AES.new(self.key, AES.MODE_EAX)
        cipher_text, tag = cipher.encrypt_and_digest(data.encode())
        full_cipher_text = cipher.nonce + tag + cipher_text
        encoded = base58.b58encode(full_cipher_text) if encode else full_cipher_text
        return encoded.decode('utf-8')

    def decrypt(self, cipher_text, encoded=True):
        cipher_text = cipher_text.encode() if isinstance(cipher_text, str) else cipher_text
        cipher_text = base58.b58decode(cipher_text) if encoded else cipher_text
        nonce = cipher_text[:16]
        tag = cipher_text[16:32]
        encrypted = cipher_text[32:]

        cipher = AES.new(self.key, AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(encrypted, tag).decode('utf-8')
