"""
Encryption utility for API keys using Fernet symmetric encryption.
"""

import os
from cryptography.fernet import Fernet
from typing import Optional

# Get encryption key from environment variable
# In production, this should be a secure, randomly generated key stored securely
ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError(
        "API_KEY_ENCRYPTION_KEY environment variable must be set. "
        "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )

# Initialize Fernet cipher
_cipher_suite = Fernet(ENCRYPTION_KEY.encode())


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key using Fernet symmetric encryption.

    Args:
        api_key: Plain text API key to encrypt

    Returns:
        Encrypted API key as a string
    """
    if not api_key:
        raise ValueError("API key cannot be empty")

    encrypted_bytes = _cipher_suite.encrypt(api_key.encode())
    return encrypted_bytes.decode()


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_api_key: Encrypted API key string

    Returns:
        Decrypted plain text API key
    """
    if not encrypted_api_key:
        raise ValueError("Encrypted API key cannot be empty")

    try:
        decrypted_bytes = _cipher_suite.decrypt(encrypted_api_key.encode())
        return decrypted_bytes.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key: {str(e)}")


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display purposes, showing only the last few characters.

    Args:
        api_key: Plain text API key to mask
        visible_chars: Number of characters to show at the end (default: 4)

    Returns:
        Masked API key string (e.g., "sk-...xyz123")
    """
    if not api_key or len(api_key) <= visible_chars:
        return "***"

    return f"{'*' * (len(api_key) - visible_chars)}{api_key[-visible_chars:]}"
