"""
Auth Core CLI - Key Generation Utility

Usage:
    python -m auth_core generate-keys <output_dir>
    python -m auth_core verify-keys <keys_dir>
"""

import sys
from pathlib import Path


def generate_keys(output_dir: str) -> None:
    """Generate Ed25519 key pair."""
    from auth_core.keys import generate_ed25519_keypair, save_keypair

    print(f"Generating Ed25519 key pair in {output_dir}...")

    private_key, _ = generate_ed25519_keypair()
    private_path, public_path = save_keypair(private_key, output_dir)

    print(f"  Private key: {private_path}")
    print(f"  Public key: {public_path}")
    print("\nDone! Keep the private key secure.")


def verify_keys(keys_dir: str) -> None:
    """Verify key pair can be loaded and used."""
    from auth_core.jwt import Ed25519Auth

    print(f"Verifying keys in {keys_dir}...")

    try:
        auth = Ed25519Auth(keys_dir=keys_dir)

        # Test token creation and verification
        test_data = {"sub": "test-user"}
        token = auth.create_access_token(test_data)
        payload = auth.verify_token(token)

        print(f"  Private key: OK")
        print(f"  Public key: OK")
        print(f"  Token creation: OK")
        print(f"  Token verification: OK")
        print(f"  Test payload: sub={payload.sub}")
        print("\nKeys are valid and working!")

    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR: Key verification failed: {e}")
        sys.exit(1)


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate-keys":
        if len(sys.argv) < 3:
            print("Usage: python -m auth_core generate-keys <output_dir>")
            sys.exit(1)
        generate_keys(sys.argv[2])

    elif command == "verify-keys":
        if len(sys.argv) < 3:
            print("Usage: python -m auth_core verify-keys <keys_dir>")
            sys.exit(1)
        verify_keys(sys.argv[2])

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
