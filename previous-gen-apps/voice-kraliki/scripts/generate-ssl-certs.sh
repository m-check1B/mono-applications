#!/bin/bash
# Generate self-signed SSL certificates for production
# In production, replace with Let's Encrypt or proper CA certificates

set -e

DOMAINS=("api.operator-demo-2026.com" "app.operator-demo-2026.com")
SSL_DIR="./nginx/ssl"

echo "🔐 Generating SSL certificates..."

# Create SSL directory
mkdir -p "$SSL_DIR"

# Generate certificates for each domain
for domain in "${DOMAINS[@]}"; do
    echo "📝 Generating certificate for $domain..."
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/$domain.key" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/$domain.key" -out "$SSL_DIR/$domain.csr" -subj "/C=US/ST=State/L=City/O=Operator Demo/OU=IT/CN=$domain"
    
    # Generate self-signed certificate (valid for 1 year)
    openssl x509 -req -days 365 -in "$SSL_DIR/$domain.csr" -signkey "$SSL_DIR/$domain.key" -out "$SSL_DIR/$domain.crt"
    
    # Clean up CSR
    rm "$SSL_DIR/$domain.csr"
    
    echo "✅ Certificate generated for $domain"
done

# Set proper permissions
chmod 600 "$SSL_DIR"/*.key
chmod 644 "$SSL_DIR"/*.crt

echo "🎉 SSL certificates generated successfully!"
echo "⚠️  NOTE: These are self-signed certificates for testing."
echo "   In production, use Let's Encrypt or purchase from a CA."