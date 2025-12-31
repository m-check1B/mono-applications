#!/bin/bash
# ============================================================================
# Development SSL Certificate Generator
# ============================================================================
# This script generates self-signed SSL certificates for local development
# of the operator-demo-multiprovider project with Traefik.
#
# Usage: ./scripts/generate-dev-certs.sh
#
# The script will create:
#   - traefik/certs/verduona.dev.crt (certificate)
#   - traefik/certs/verduona.dev.key (private key)
#   - traefik/certs/ca.crt (CA certificate for importing to system/browser)
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="verduona.dev"
CERT_DIR="$(dirname "$0")/../traefik/certs"
VALIDITY_DAYS=825  # Maximum validity for modern browsers

echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}Development SSL Certificate Generator${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""

# Create certificate directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [ -f "$CERT_DIR/$DOMAIN.crt" ] && [ -f "$CERT_DIR/$DOMAIN.key" ]; then
    echo -e "${YELLOW}Certificates already exist in $CERT_DIR${NC}"
    read -p "Do you want to regenerate them? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Keeping existing certificates.${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}Generating SSL certificates for development...${NC}"
echo ""

# Generate CA private key
echo -e "${YELLOW}[1/6] Generating CA private key...${NC}"
openssl genrsa -out "$CERT_DIR/ca.key" 4096

# Generate CA certificate
echo -e "${YELLOW}[2/6] Generating CA certificate...${NC}"
openssl req -x509 -new -nodes -key "$CERT_DIR/ca.key" -sha256 -days "$VALIDITY_DAYS" -out "$CERT_DIR/ca.crt" \
    -subj "/C=US/ST=Development/L=Local/O=Operator Demo/OU=Development/CN=Operator Demo Development CA"

# Generate private key for domain
echo -e "${YELLOW}[3/6] Generating private key for $DOMAIN...${NC}"
openssl genrsa -out "$CERT_DIR/$DOMAIN.key" 2048

# Create certificate signing request (CSR)
echo -e "${YELLOW}[4/6] Creating certificate signing request...${NC}"
openssl req -new -key "$CERT_DIR/$DOMAIN.key" -out "$CERT_DIR/$DOMAIN.csr" \
    -subj "/C=US/ST=Development/L=Local/O=Operator Demo/OU=Development/CN=*.$DOMAIN"

# Create extensions file for SAN (Subject Alternative Names)
cat > "$CERT_DIR/$DOMAIN.ext" << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = *.$DOMAIN
DNS.3 = operator.$DOMAIN
DNS.4 = api.$DOMAIN
DNS.5 = docs.$DOMAIN
DNS.6 = traefik.$DOMAIN
DNS.7 = pgadmin.$DOMAIN
DNS.8 = redis.$DOMAIN
DNS.9 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Generate certificate signed by CA
echo -e "${YELLOW}[5/6] Generating certificate signed by CA...${NC}"
openssl x509 -req -in "$CERT_DIR/$DOMAIN.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial -out "$CERT_DIR/$DOMAIN.crt" -days "$VALIDITY_DAYS" -sha256 \
    -extfile "$CERT_DIR/$DOMAIN.ext"

# Set proper permissions
echo -e "${YELLOW}[6/6] Setting permissions...${NC}"
chmod 644 "$CERT_DIR/$DOMAIN.crt"
chmod 600 "$CERT_DIR/$DOMAIN.key"
chmod 644 "$CERT_DIR/ca.crt"
chmod 600 "$CERT_DIR/ca.key"

# Clean up temporary files
rm -f "$CERT_DIR/$DOMAIN.csr" "$CERT_DIR/$DOMAIN.ext" "$CERT_DIR/ca.srl"

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}Certificates generated successfully!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "Certificate files created in: ${GREEN}$CERT_DIR${NC}"
echo ""
echo "  - $DOMAIN.crt (Certificate)"
echo "  - $DOMAIN.key (Private Key)"
echo "  - ca.crt (CA Certificate)"
echo ""
echo -e "${YELLOW}To use these certificates with HTTPS in your browser:${NC}"
echo ""
echo "1. Trust the CA certificate:"
echo ""
echo -e "   ${GREEN}macOS:${NC}"
echo "   sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $CERT_DIR/ca.crt"
echo ""
echo -e "   ${GREEN}Linux (Ubuntu/Debian):${NC}"
echo "   sudo cp $CERT_DIR/ca.crt /usr/local/share/ca-certificates/operator-demo-ca.crt"
echo "   sudo update-ca-certificates"
echo ""
echo -e "   ${GREEN}Firefox:${NC}"
echo "   Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import"
echo "   Then select: $CERT_DIR/ca.crt"
echo ""
echo -e "   ${GREEN}Chrome/Edge:${NC}"
echo "   Settings → Privacy and Security → Security → Manage Certificates → Authorities → Import"
echo "   Then select: $CERT_DIR/ca.crt"
echo ""
echo "2. Add hostnames to /etc/hosts:"
echo ""
echo "   sudo tee -a /etc/hosts > /dev/null << EOF"
echo "   127.0.0.1 operator.verduona.dev"
echo "   127.0.0.1 api.verduona.dev"
echo "   127.0.0.1 docs.verduona.dev"
echo "   127.0.0.1 traefik.verduona.dev"
echo "   127.0.0.1 pgadmin.verduona.dev"
echo "   127.0.0.1 redis.verduona.dev"
echo "EOF"
echo ""
echo "3. Start services with Traefik:"
echo ""
echo "   docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d"
echo ""
echo -e "${GREEN}You should now be able to access:${NC}"
echo ""
echo "  - https://operator.verduona.dev (Frontend)"
echo "  - https://api.verduona.dev (Backend API)"
echo "  - https://docs.verduona.dev (API Documentation)"
echo "  - https://traefik.verduona.dev (Traefik Dashboard)"
echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
