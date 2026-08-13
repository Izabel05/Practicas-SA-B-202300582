import base64
import hashlib
import hmac
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config.settings import Settings


class DataEncryptionService:
    """Cifra datos sensibles y genera indices de busqueda seguros."""

    _NONCE_SIZE = 12

    def __init__(self) -> None:
        self._encryption_key = self._decode_key(
            Settings.DATA_ENCRYPTION_KEY,
            "DATA_ENCRYPTION_KEY",
        )
        self._search_key = self._decode_key(
            Settings.DATA_SEARCH_KEY,
            "DATA_SEARCH_KEY",
        )

        if self._encryption_key == self._search_key:
            raise RuntimeError(
                "DATA_ENCRYPTION_KEY y DATA_SEARCH_KEY deben ser diferentes."
            )

        self._aesgcm = AESGCM(self._encryption_key)

    def encrypt(self, value: str) -> str:
        nonce = os.urandom(self._NONCE_SIZE)
        ciphertext = self._aesgcm.encrypt(
            nonce, value.encode("utf-8"), None
        )
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, encrypted_value: str) -> str:
        encrypted_data = base64.urlsafe_b64decode(
            encrypted_value.encode("ascii")
        )
        nonce = encrypted_data[: self._NONCE_SIZE]
        ciphertext = encrypted_data[self._NONCE_SIZE :]

        if not ciphertext:
            raise ValueError("El dato cifrado no tiene un formato valido.")

        return self._aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")

    def create_search_hash(self, value: str) -> str:
        normalized_value = value.strip().lower().encode("utf-8")
        return hmac.new(
            self._search_key, normalized_value, hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _decode_key(encoded_key: str, variable_name: str) -> bytes:
        try:
            key = base64.urlsafe_b64decode(encoded_key.encode("ascii"))
        except Exception as error:
            raise RuntimeError(
                f"{variable_name} debe estar codificada en Base64 URL-safe."
            ) from error

        if len(key) != 32:
            raise RuntimeError(
                f"{variable_name} debe representar exactamente 32 bytes."
            )

        return key
