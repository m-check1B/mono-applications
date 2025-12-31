#!/usr/bin/env python3
"""
Test Stripe links configuration in landing page
"""

import re
import sys
from pathlib import Path


def test_stripe_links():
    """Verify Stripe payment links are properly configured"""

    project_root = Path(__file__).parent.parent
    landing_page = project_root / "docs" / "landing-page.html"

    if not landing_page.exists():
        print("❌ Landing page not found")
        return False

    content = landing_page.read_text()

    # Check for placeholder links
    placeholder_pattern = r"https://buy\.stripe\.com/placeholder_"
    has_placeholders = re.search(placeholder_pattern, content)

    # Count Stripe payment links
    stripe_links = re.findall(r'https://buy\.stripe\.com/[^\s"\']+', content)

    # Count email links for enterprise
    email_links = re.findall(
        r"mailto:sales@verduona\.com\?subject=Magic%20Box%20Enterprise%20Inquiry",
        content,
    )

    print("=== Stripe Links Configuration Test ===\n")

    print(f"Total Stripe payment links found: {len(stripe_links)}")
    print(f"Enterprise email links found: {len(email_links)}")

    if has_placeholders:
        print("⚠️  Warning: Placeholder Stripe links detected")
        print("   Run ./scripts/configure_stripe_links.sh to configure real links")
        print("   Or add STRIPE_PAYMENT_LINK_* to .env")
        return False
    else:
        print("✓ No placeholder links found")

    # Verify we have links for all tiers
    if len(stripe_links) >= 2:  # Starter and Pro
        print("✓ Multiple payment links configured")

    if len(email_links) >= 1:
        print("✓ Enterprise contact link present")

    print("\n✅ Stripe links configuration looks good!")
    return True


if __name__ == "__main__":
    success = test_stripe_links()
    sys.exit(0 if success else 1)
