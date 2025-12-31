"""
Ed25519 Key Management Utilities

Generate, load, and save Ed25519 key pairs for JWT signing.
"""

from pathlib import Path
from typing import Tuple, Optional, Union

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_ed25519_keypair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """
    Generate a new Ed25519 key pair.

    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def load_private_key(
    path: Union[str, Path],
    password: Optional[bytes] = None,
) -> ed25519.Ed25519PrivateKey:
    """
    Load Ed25519 private key from PEM file.

    Args:
        path: Path to private key PEM file
        password: Optional password for encrypted keys

    Returns:
        Ed25519PrivateKey

    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If key format is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Private key not found at {path}. "
            "Run: auth-core generate-keys <output_dir>"
        )

    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=password,
        )

    if not isinstance(key, ed25519.Ed25519PrivateKey):
        raise ValueError(f"Expected Ed25519 private key, got {type(key)}")

    return key


def load_public_key(path: Union[str, Path]) -> ed25519.Ed25519PublicKey:
    """
    Load Ed25519 public key from PEM file.

    Args:
        path: Path to public key PEM file

    Returns:
        Ed25519PublicKey

    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If key format is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Public key not found at {path}. "
            "Run: auth-core generate-keys <output_dir>"
        )

    with open(path, "rb") as f:
        key = serialization.load_pem_public_key(f.read())

    if not isinstance(key, ed25519.Ed25519PublicKey):
        raise ValueError(f"Expected Ed25519 public key, got {type(key)}")

    return key


def save_keypair(
    private_key: ed25519.Ed25519PrivateKey,
    output_dir: Union[str, Path],
    private_name: str = "jwt_private.pem",
    public_name: str = "jwt_public.pem",
    password: Optional[bytes] = None,
) -> Tuple[Path, Path]:
    """
    Save Ed25519 key pair to PEM files.

    Args:
        private_key: Ed25519 private key
        output_dir: Directory to save keys
        private_name: Filename for private key
        public_name: Filename for public key
        password: Optional password to encrypt private key

    Returns:
        Tuple of (private_key_path, public_key_path)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    private_path = output_dir / private_name
    public_path = output_dir / public_name

    # Serialize private key
    if password:
        encryption = serialization.BestAvailableEncryption(password)
    else:
        encryption = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )

    # Serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Write files with restrictive permissions
    private_path.write_bytes(private_pem)
    private_path.chmod(0o600)  # Owner read/write only

    public_path.write_bytes(public_pem)
    public_path.chmod(0o644)  # Owner read/write, others read

    return private_path, public_path


def private_key_to_pem(
    private_key: ed25519.Ed25519PrivateKey,
    password: Optional[bytes] = None,
) -> bytes:
    """
    Serialize private key to PEM format.

    Args:
        private_key: Ed25519 private key
        password: Optional password for encryption

    Returns:
        PEM-encoded private key bytes
    """
    if password:
        encryption = serialization.BestAvailableEncryption(password)
    else:
        encryption = serialization.NoEncryption()

    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )


def public_key_to_pem(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """
    Serialize public key to PEM format.

    Args:
        public_key: Ed25519 public key

    Returns:
        PEM-encoded public key bytes
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
