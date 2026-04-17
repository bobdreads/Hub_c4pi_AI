import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from config import settings
from utils.logging import get_logger

log = get_logger("utils.crypto")


def _get_key() -> bytes:
    key = settings.api_key_master.encode("utf-8")
    # Garante 32 bytes para AES-256
    return key[:32].ljust(32, b"0")


def encrypt(plaintext: str) -> str:
    key = _get_key()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding para múltiplo de 16 bytes
    data = plaintext.encode("utf-8")
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)

    encrypted = encryptor.update(data) + encryptor.finalize()
    result = base64.b64encode(iv + encrypted).decode("utf-8")
    return result


def decrypt(ciphertext: str) -> str:
    key = _get_key()
    raw = base64.b64decode(ciphertext.encode("utf-8"))
    iv = raw[:16]
    encrypted = raw[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    data = decryptor.update(encrypted) + decryptor.finalize()
    pad_len = data[-1]
    return data[:-pad_len].decode("utf-8")
