import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from ..errors import CredentialInvalidError, CredentialMissingError


def _fernet(secret: str | None) -> Fernet:
    if not secret:
        raise CredentialMissingError("CREDENTIAL_ENCRYPTION_KEY is not configured")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
    return Fernet(key)


def encrypt_credential(value: str, secret: str | None) -> str:
    if not value:
        raise CredentialMissingError("credential is required")
    return _fernet(secret).encrypt(value.encode()).decode()


def decrypt_credential(value: str | None, secret: str | None) -> str | None:
    if not value:
        return None
    try:
        return _fernet(secret).decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise CredentialInvalidError("stored credential cannot be decrypted") from exc


def mask_credential(value: str | None) -> str | None:
    if not value:
        return None
    return f"{value[:3]}••••{value[-3:]}" if len(value) >= 8 else "••••••••"
