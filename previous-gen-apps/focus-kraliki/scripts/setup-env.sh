#!/usr/bin/env bash
#
# Focus by Kraliki Environment Setup Helper
# Generates secure random values for environment variables
#
# Usage:
#   ./scripts/setup-env.sh           # Generate all required secrets
#   ./scripts/setup-env.sh oauth     # Generate only OAuth tokens
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if OpenSSL is available
if ! command -v openssl &> /dev/null; then
    print_error "OpenSSL is required but not installed"
    exit 1
fi

# Generate JWT Secret
generate_jwt_secret() {
    print_header "Generating JWT Secret"
    jwt_secret=$(openssl rand -hex 32)
    echo "JWT_SECRET=$jwt_secret"
    echo ""
}

# Generate Session Secret
generate_session_secret() {
    print_header "Generating Session Secret"
    session_secret=$(openssl rand -hex 32)
    echo "SESSION_SECRET=$session_secret"
    echo ""
}

# Generate Google Calendar Webhook Token
generate_webhook_token() {
    print_header "Generating Google Calendar Webhook Token"
    webhook_token=$(openssl rand -hex 32)
    echo "GOOGLE_CALENDAR_WEBHOOK_TOKEN=$webhook_token"
    echo ""
}

# Generate Redis Password
generate_redis_password() {
    print_header "Generating Redis Password"
    redis_password=$(openssl rand -base64 32 | tr -d '/+=')
    echo "REDIS_PASSWORD=$redis_password"
    echo ""
}

# Generate Database Password
generate_db_password() {
    print_header "Generating Database Password"
    db_password=$(openssl rand -base64 32 | tr -d '/+=')
    echo "DB_PASSWORD=$db_password"
    echo ""
}

# Generate II-Agent Webhook Secret
generate_ii_agent_secret() {
    print_header "Generating II-Agent Webhook Secret"
    ii_agent_secret=$(openssl rand -hex 32)
    echo "II_AGENT_WEBHOOK_SECRET=$ii_agent_secret"
    echo ""
}

# Display Google OAuth setup instructions
display_oauth_setup() {
    print_header "Google OAuth Setup Instructions"
    echo ""
    echo "To complete Google OAuth setup, follow these steps:"
    echo ""
    echo "1. Go to Google Cloud Console: https://console.cloud.google.com/"
    echo "2. Create a new project or select an existing one"
    echo "3. Enable the following APIs:"
    echo "   - Google Calendar API"
    echo "   - Google+ API"
    echo ""
    echo "4. Configure OAuth consent screen (External user type)"
    echo "5. Create OAuth 2.0 credentials (Web application)"
    echo ""
    echo "6. Add these Authorized redirect URIs:"
    echo "   - https://your-domain.com/auth/google/callback"
    echo "   - https://api.yourdomain.com/auth/google/callback"
    echo ""
    echo "7. Copy the Client ID and Client Secret and add to your .env file:"
    echo ""
    echo -e "${YELLOW}GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com${NC}"
    echo -e "${YELLOW}GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here${NC}"
    echo ""
    echo "For complete details, see: docs/GOOGLE_OAUTH_SETUP.md"
    echo ""
}

# Main function
main() {
    print_header "Focus by Kraliki Environment Setup Helper"
    echo ""
    echo "This script generates secure environment variable values"
    echo "and provides setup instructions for external services."
    echo ""

    # Parse command line arguments
    case "${1:-all}" in
        all)
            generate_jwt_secret
            generate_session_secret
            generate_webhook_token
            generate_redis_password
            generate_db_password
            generate_ii_agent_secret
            display_oauth_setup
            ;;
        oauth)
            generate_webhook_token
            display_oauth_setup
            ;;
        jwt)
            generate_jwt_secret
            generate_session_secret
            ;;
        secrets)
            generate_jwt_secret
            generate_session_secret
            generate_webhook_token
            generate_ii_agent_secret
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  all      - Generate all secrets and show OAuth setup (default)"
            echo "  oauth     - Generate OAuth-related tokens and show OAuth setup"
            echo "  jwt      - Generate JWT and session secrets"
            echo "  secrets  - Generate webhook and secrets"
            echo ""
            exit 1
            ;;
    esac

    print_header "Next Steps"
    echo ""
    echo "1. Copy the generated values to your .env file:"
    echo "   cp .env.prod.template .env"
    echo "   nano .env  # Paste the values and fill in other required fields"
    echo ""
    echo "2. Complete Google OAuth setup (see above instructions)"
    echo ""
    echo "3. Deploy with: docker-compose -f docker-compose.prod.yml up -d"
    echo ""
    print_success "Environment setup complete!"
}

# Run main function
main "$@"
