import base64

from app.config.settings import Settings
from app.service.data_encryption_service import DataEncryptionService


def _configure_test_keys() -> None:
    Settings.DATA_ENCRYPTION_KEY = base64.urlsafe_b64encode(
        bytes(range(32))
    ).decode("ascii")
    Settings.DATA_SEARCH_KEY = base64.urlsafe_b64encode(
        bytes(range(32, 64))
    ).decode("ascii")


def test_encrypts_and_decrypts_sensitive_data() -> None:
    _configure_test_keys()
    service = DataEncryptionService()
    plaintext = "Paula Ejemplo"
    encrypted = service.encrypt(plaintext)

    assert encrypted != plaintext
    assert plaintext not in encrypted
    assert service.decrypt(encrypted) == plaintext


def test_aes_gcm_uses_a_different_nonce_each_time() -> None:
    _configure_test_keys()
    service = DataEncryptionService()

    assert service.encrypt("dato") != service.encrypt("dato")


def test_search_hash_is_normalized_and_deterministic() -> None:
    _configure_test_keys()
    service = DataEncryptionService()

    first_hash = service.create_search_hash(" User@Example.com ")
    second_hash = service.create_search_hash("user@example.com")

    assert first_hash == second_hash
    assert len(first_hash) == 64
