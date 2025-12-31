#!/usr/bin/env bash
#
# configure_stripe_links.sh
# 
# Inject Stripe payment links from .env into landing page
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Magic Box Stripe Links Configuration ===${NC}"
echo ""

# Load .env file
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    echo -e "${RED}Error: .env file not found at ${PROJECT_ROOT}/.env${NC}"
    echo "Please create .env from .env.example first"
    exit 1
fi

# Source the .env file
set -a
source "${PROJECT_ROOT}/.env"
set +a

# Check if Stripe links are configured
if [ -z "$STRIPE_PAYMENT_LINK_STARTER" ] && [ -z "$STRIPE_PAYMENT_LINK_PRO" ] && [ -z "$STRIPE_PAYMENT_LINK_ENTERPRISE" ]; then
    echo -e "${YELLOW}Warning: No Stripe payment links configured in .env${NC}"
    echo "Links will remain as placeholders"
    echo ""
    echo "To configure, add these to your .env:"
    echo "  STRIPE_PAYMENT_LINK_STARTER=https://buy.stripe.com/..."
    echo "  STRIPE_PAYMENT_LINK_PRO=https://buy.stripe.com/..."
    echo "  STRIPE_PAYMENT_LINK_ENTERPRISE=https://buy.stripe.com/..."
    echo ""
    echo "Create payment links in Stripe Dashboard:"
    echo "  https://dashboard.stripe.com/products/payment-links"
fi

# Default values (placeholders)
STARTER_LINK="${STRIPE_PAYMENT_LINK_STARTER:-https://buy.stripe.com/placeholder_magic_box_starter}"
PRO_LINK="${STRIPE_PAYMENT_LINK_PRO:-https://buy.stripe.com/placeholder_magic_box_pro}"
ENTERPRISE_LINK="${STRIPE_PAYMENT_LINK_ENTERPRISE:-mailto:sales@verduona.com?subject=Magic%20Box%20Enterprise%20Inquiry}"

# Find landing page
LANDING_PAGE="${PROJECT_ROOT}/docs/landing-page.html"

if [ ! -f "$LANDING_PAGE" ]; then
    echo -e "${RED}Error: Landing page not found at $LANDING_PAGE${NC}"
    exit 1
fi

# Create backup
cp "$LANDING_PAGE" "${LANDING_PAGE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ Created backup${NC}"

# Replace Stripe links in landing page
echo -e "${GREEN}Updating Stripe links...${NC}"
echo "  Starter: $STARTER_LINK"
echo "  Pro: $PRO_LINK"
echo "  Enterprise: $ENTERPRISE_LINK"
echo ""

# Use sed to replace the links
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed
    sed -i '' "s|https://buy\.stripe\.com/placeholder_magic_box_starter|$STARTER_LINK|g" "$LANDING_PAGE"
    sed -i '' "s|https://buy\.stripe\.com/placeholder_magic_box_pro|$PRO_LINK|g" "$LANDING_PAGE"
    # Enterprise goes to email by default (custom pricing)
    if [ -n "$STRIPE_PAYMENT_LINK_ENTERPRISE" ]; then
        sed -i '' "s|mailto:sales@verduona\.com?subject=Magic%20Box%20Enterprise%20Inquiry|$ENTERPRISE_LINK|g" "$LANDING_PAGE"
    fi
else
    # Linux sed
    sed -i "s|https://buy\.stripe\.com/placeholder_magic_box_starter|$STARTER_LINK|g" "$LANDING_PAGE"
    sed -i "s|https://buy\.stripe\.com/placeholder_magic_box_pro|$PRO_LINK|g" "$LANDING_PAGE"
    # Enterprise goes to email by default (custom pricing)
    if [ -n "$STRIPE_PAYMENT_LINK_ENTERPRISE" ]; then
        sed -i "s|mailto:sales@verduona\.com?subject=Magic%20Box%20Enterprise%20Inquiry|$ENTERPRISE_LINK|g" "$LANDING_PAGE"
    fi
fi

echo -e "${GREEN}✓ Landing page updated${NC}"
echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  Starter link: $STARTER_LINK"
echo "  Pro link: $PRO_LINK"
if [ -n "$STRIPE_PAYMENT_LINK_ENTERPRISE" ]; then
    echo "  Enterprise link: $ENTERPRISE_LINK"
else
    echo "  Enterprise: Contact sales (custom pricing)"
fi
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Deploy landing page to production"
echo "  2. Test payment links work correctly"
echo "  3. Verify Stripe checkout flow"
