"""Tests for Ed25519 key management."""

import pytest
import tempfile
from pathlib import Path

from auth_core.keys import (
    generate_ed25519_keypair,
    save_keypair,
    load_private_key,
    load_public_key,
    private_key_to_pem,
    public_key_to_pem,
)


class TestKeyGeneration:
    """Test key generation."""

    def test_generate_keypair(self):
        """Should generate valid Ed25519 key pair."""
        private_key, public_key = generate_ed25519_keypair()

        assert private_key is not None
        assert public_key is not None

    def test_keypair_can_sign_and_verify(self):
        """Generated keys should work for signing/verification."""
        private_key, public_key = generate_ed25519_keypair()

        # Sign some data
        message = b"test message"
        signature = private_key.sign(message)

        # Verify with public key
        public_key.verify(signature, message)  # Raises if invalid

    def test_multiple_keypairs_are_unique(self):
        """Each generated key pair should be unique."""
        private1, public1 = generate_ed25519_keypair()
        private2, public2 = generate_ed25519_keypair()

        pem1 = private_key_to_pem(private1)
        pem2 = private_key_to_pem(private2)

        assert pem1 != pem2


class TestKeySerialization:
    """Test key serialization."""

    def test_private_key_to_pem(self):
        """Should serialize private key to PEM."""
        private_key, _ = generate_ed25519_keypair()
        pem = private_key_to_pem(private_key)

        assert pem.startswith(b"-----BEGIN PRIVATE KEY-----")
        assert pem.endswith(b"-----END PRIVATE KEY-----\n")

    def test_public_key_to_pem(self):
        """Should serialize public key to PEM."""
        _, public_key = generate_ed25519_keypair()
        pem = public_key_to_pem(public_key)

        assert pem.startswith(b"-----BEGIN PUBLIC KEY-----")
        assert pem.endswith(b"-----END PUBLIC KEY-----\n")


class TestKeyPersistence:
    """Test key save/load operations."""

    def test_save_and_load_keypair(self):
        """Should save and load key pair correctly."""
        private_key, _ = generate_ed25519_keypair()

        with tempfile.TemporaryDirectory() as tmpdir:
            private_path, public_path = save_keypair(private_key, tmpdir)

            assert private_path.exists()
            assert public_path.exists()

            # Load and verify
            loaded_private = load_private_key(private_path)
            loaded_public = load_public_key(public_path)

            # Sign with original, verify with loaded
            message = b"test"
            signature = private_key.sign(message)
            loaded_public.verify(signature, message)

            # Sign with loaded, verify with original
            signature2 = loaded_private.sign(message)
            public_key = private_key.public_key()
            public_key.verify(signature2, message)

    def test_private_key_permissions(self):
        """Private key should have restrictive permissions."""
        private_key, _ = generate_ed25519_keypair()

        with tempfile.TemporaryDirectory() as tmpdir:
            private_path, _ = save_keypair(private_key, tmpdir)

            # Check permissions (Unix only)
            import os
            mode = os.stat(private_path).st_mode & 0o777
            assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"

    def test_load_nonexistent_private_key(self):
        """Should raise FileNotFoundError for missing private key."""
        with pytest.raises(FileNotFoundError) as exc:
            load_private_key("/nonexistent/path/key.pem")

        assert "Private key not found" in str(exc.value)

    def test_load_nonexistent_public_key(self):
        """Should raise FileNotFoundError for missing public key."""
        with pytest.raises(FileNotFoundError) as exc:
            load_public_key("/nonexistent/path/key.pem")

        assert "Public key not found" in str(exc.value)

    def test_custom_key_names(self):
        """Should support custom key file names."""
        private_key, _ = generate_ed25519_keypair()

        with tempfile.TemporaryDirectory() as tmpdir:
            private_path, public_path = save_keypair(
                private_key,
                tmpdir,
                private_name="custom_private.pem",
                public_name="custom_public.pem",
            )

            assert private_path.name == "custom_private.pem"
            assert public_path.name == "custom_public.pem"
