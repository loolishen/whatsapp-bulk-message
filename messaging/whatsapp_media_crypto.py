"""
WhatsApp encrypted media (.enc) decryption helpers.

Baileys/WABot webhooks often provide:
- imageMessage.url / directPath (download encrypted bytes)
- imageMessage.mediaKey (base64)
- fileSha256 / fileEncSha256 (base64)
- mimetype

WhatsApp media encryption format (simplified):
encFile = ciphertext || mac10
mac10 = HMAC-SHA256(macKey, iv || ciphertext)[:10]
ciphertext is AES-256-CBC(cipherKey, iv, plaintext with PKCS7 padding)

Keys are derived via HKDF (HMAC-SHA256) from mediaKey with info string
e.g. "WhatsApp Image Keys", producing 112 bytes:
iv(16) | cipherKey(32) | macKey(32) | refKey(32)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


_HKDF_SALT_32_ZERO = b"\x00" * 32


def _b64decode_maybe(s: Optional[str]) -> Optional[bytes]:
    if not s:
        return None
    try:
        # WhatsApp fields are typically standard base64 (not URL-safe)
        return base64.b64decode(s)
    except Exception:
        # Best-effort fallback
        try:
            return base64.b64decode(s + "===")
        except Exception:
            return None


def hkdf_sha256(ikm: bytes, length: int, info: bytes, salt: bytes = _HKDF_SALT_32_ZERO) -> bytes:
    """
    HKDF (RFC 5869) using SHA-256.
    """
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    t = b""
    okm = b""
    counter = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:length]


@dataclass(frozen=True)
class WhatsAppMediaKeys:
    iv: bytes
    cipher_key: bytes
    mac_key: bytes
    ref_key: bytes


def derive_whatsapp_media_keys(media_key: bytes, media_info: str) -> WhatsAppMediaKeys:
    okm = hkdf_sha256(media_key, 112, info=media_info.encode("utf-8"))
    iv = okm[0:16]
    cipher_key = okm[16:48]
    mac_key = okm[48:80]
    ref_key = okm[80:112]
    return WhatsAppMediaKeys(iv=iv, cipher_key=cipher_key, mac_key=mac_key, ref_key=ref_key)


def decrypt_whatsapp_media(enc_bytes: bytes, media_key_b64: str, media_info: str, expected_file_sha256_b64: Optional[str] = None) -> bytes:
    """
    Decrypt WhatsApp encrypted media bytes.
    Raises ValueError on validation failures.
    """
    if not enc_bytes or len(enc_bytes) < 16 + 10:
        raise ValueError("Encrypted media content too small")

    media_key = _b64decode_maybe(media_key_b64)
    if not media_key:
        raise ValueError("Missing/invalid mediaKey")

    keys = derive_whatsapp_media_keys(media_key, media_info=media_info)

    # Split ciphertext and 10-byte MAC
    ciphertext = enc_bytes[:-10]
    mac10 = enc_bytes[-10:]

    mac_calc = hmac.new(keys.mac_key, keys.iv + ciphertext, hashlib.sha256).digest()[:10]
    if mac_calc != mac10:
        raise ValueError("Encrypted media MAC validation failed")

    cipher = AES.new(keys.cipher_key, AES.MODE_CBC, iv=keys.iv)
    padded_plain = cipher.decrypt(ciphertext)
    try:
        plain = unpad(padded_plain, 16)
    except ValueError:
        # If padding is off, surface a clearer message
        raise ValueError("Encrypted media padding invalid (cannot decrypt)")

    # Optional integrity check against fileSha256 (plaintext sha256)
    expected_sha = _b64decode_maybe(expected_file_sha256_b64) if expected_file_sha256_b64 else None
    if expected_sha:
        actual_sha = hashlib.sha256(plain).digest()
        if actual_sha != expected_sha:
            raise ValueError("Decrypted media SHA256 mismatch")

    return plain


