#!/bin/bash
# Generate Ed25519 JWT signing keys for Focus by Kraliki
# Stack 2026 compliant asymmetric authentication

set -e

KEYS_DIR="keys"
PRIVATE_KEY="${KEYS_DIR}/jwt_private.pem"
PUBLIC_KEY="${KEYS_DIR}/jwt_public.pem"

echo "🔐 Generating Ed25519 JWT keys for Stack 2026 compliance..."

# Create keys directory
mkdir -p "${KEYS_DIR}"

# Generate private key
openssl genpkey -algorithm ED25519 -out "${PRIVATE_KEY}"
echo "✅ Private key generated: ${PRIVATE_KEY}"

# Extract public key
openssl pkey -in "${PRIVATE_KEY}" -pubout -out "${PUBLIC_KEY}"
echo "✅ Public key generated: ${PUBLIC_KEY}"

# Secure private key (owner read-only)
chmod 600 "${PRIVATE_KEY}"
chmod 644 "${PUBLIC_KEY}"

echo ""
echo "🎉 Ed25519 key pair generated successfully!"
echo ""
echo "📝 Keys saved to:"
echo "   Private: ${PRIVATE_KEY} (chmod 600)"
echo "   Public:  ${PUBLIC_KEY} (chmod 644)"
echo ""
echo "⚠️  IMPORTANT: Add 'keys/' to .gitignore to prevent committing private keys!"
echo ""
