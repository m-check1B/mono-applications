#!/usr/bin/env python3
"""
Stripe Products Setup Script for Voice by Kraliki
Creates products and prices for both CC-Lite (B2B) and Voice of People (B2C)

Usage:
    python3 setup_stripe_products.py                    # Create all products
    python3 setup_stripe_products.py --test             # Create in test mode
    python3 setup_stripe_products.py --list             # List existing products
"""

import os
import sys
import argparse
import stripe


def setup_stripe(test_mode: bool = False):
    """Create Stripe products and prices"""

    if test_mode:
        print("=" * 60)
        print("TEST MODE - Using Stripe test keys")
        print("=" * 60)
        stripe.api_key = os.getenv("STRIPE_TEST_SECRET_KEY", "sk_test_...")
    else:
        print("=" * 60)
        print("PRODUCTION MODE - Using Stripe live keys")
        print("=" * 60)
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_live_...")

    if (
        not stripe.api_key
        or stripe.api_key.startswith("sk_test_")
        or stripe.api_key.startswith("sk_live_")
    ):
        print(f"\nUsing Stripe API key: {stripe.api_key[:8]}...{stripe.api_key[-4:]}")
    else:
        print(
            "\nERROR: Stripe API key not found. Set STRIPE_SECRET_KEY or STRIPE_TEST_SECRET_KEY environment variable."
        )
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Creating CC-Lite (B2B) Products")
    print("=" * 60)

    # CC-Lite Starter
    try:
        product = stripe.Product.create(
            name="CC-Lite Starter",
            description="Up to 5 agents, 1,000 AI minutes/month",
            metadata={"product": "cc_lite", "plan": "starter"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=150000,  # $1500.00 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"product": "cc_lite", "plan": "starter"},
        )
        print(f"\n✓ CC-Lite Starter created")
        print(f"  Product ID: {product.id}")
        print(f"  Price ID: {price.id}")
        print(f"  Price: ${price.unit_amount / 100:.2f}/month")
    except Exception as e:
        print(f"\n✗ Error creating CC-Lite Starter: {e}")

    # CC-Lite Professional
    try:
        product = stripe.Product.create(
            name="CC-Lite Professional",
            description="Up to 15 agents, 3,000 AI minutes/month",
            metadata={"product": "cc_lite", "plan": "professional"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=350000,  # $3500.00 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"product": "cc_lite", "plan": "professional"},
        )
        print(f"\n✓ CC-Lite Professional created")
        print(f"  Product ID: {product.id}")
        print(f"  Price ID: {price.id}")
        print(f"  Price: ${price.unit_amount / 100:.2f}/month")
    except Exception as e:
        print(f"\n✗ Error creating CC-Lite Professional: {e}")

    print("\n" + "=" * 60)
    print("Creating Voice of People (B2C) Products")
    print("=" * 60)

    # Voice of People Personal
    try:
        product = stripe.Product.create(
            name="Voice of People - Personal",
            description="100 AI voice minutes/month, full features",
            metadata={"product": "vop", "plan": "personal"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=999,  # $9.99 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"product": "vop", "plan": "personal"},
        )
        print(f"\n✓ Voice of People Personal created")
        print(f"  Product ID: {product.id}")
        print(f"  Price ID: {price.id}")
        print(f"  Price: ${price.unit_amount / 100:.2f}/month")
    except Exception as e:
        print(f"\n✗ Error creating Voice of People Personal: {e}")

    # Voice of People Premium
    try:
        product = stripe.Product.create(
            name="Voice of People - Premium",
            description="500 AI voice minutes/month, priority support",
            metadata={"product": "vop", "plan": "premium"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=2999,  # $29.99 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"product": "vop", "plan": "premium"},
        )
        print(f"\n✓ Voice of People Premium created")
        print(f"  Product ID: {product.id}")
        print(f"  Price ID: {price.id}")
        print(f"  Price: ${price.unit_amount / 100:.2f}/month")
    except Exception as e:
        print(f"\n✗ Error creating Voice of People Premium: {e}")

    # Voice of People Pro
    try:
        product = stripe.Product.create(
            name="Voice of People - Pro",
            description="2,000 AI voice minutes/month, API access, business license",
            metadata={"product": "vop", "plan": "pro"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=9999,  # $99.99 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"product": "vop", "plan": "pro"},
        )
        print(f"\n✓ Voice of People Pro created")
        print(f"  Product ID: {product.id}")
        print(f"  Price ID: {price.id}")
        print(f"  Price: ${price.unit_amount / 100:.2f}/month")
    except Exception as e:
        print(f"\n✗ Error creating Voice of People Pro: {e}")

    print("\n" + "=" * 60)
    print("Environment Variables to Set")
    print("=" * 60)
    print("\n# CC-Lite (B2B) Price IDs")
    print("STRIPE_PRICE_ID_CCLITE_STARTER=price_cclite_starter_1500")
    print("STRIPE_PRICE_ID_CCLITE_PROFESSIONAL=price_cclite_pro_3500")
    print("\n# Voice of People (B2C) Price IDs")
    print("STRIPE_PRICE_ID_VOP_PERSONAL=price_vop_personal_999")
    print("STRIPE_PRICE_ID_VOP_PREMIUM=price_vop_premium_2999")
    print("STRIPE_PRICE_ID_VOP_PRO=price_vop_pro_9999")
    print("\nReplace the placeholder IDs with the actual Price IDs above.")
    print("\n" + "=" * 60)


def list_products(test_mode: bool = False):
    """List existing Stripe products"""

    if test_mode:
        stripe.api_key = os.getenv("STRIPE_TEST_SECRET_KEY")
    else:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    if not stripe.api_key:
        print("ERROR: Stripe API key not found.")
        sys.exit(1)

    print("\nExisting Stripe Products:")
    print("=" * 80)

    products = stripe.Product.list(limit=100)
    for product in products.auto_paging_iter():
        print(f"\n{product.name}")
        print(f"  ID: {product.id}")
        print(f"  Description: {product.description or 'N/A'}")
        print(f"  Metadata: {product.metadata}")

        # List prices for this product
        prices = stripe.Price.list(product=product.id, limit=10)
        for price in prices.auto_paging_iter():
            print(f"\n  Price ID: {price.id}")
            if price.recurring:
                print(f"    ${price.unit_amount / 100:.2f}/{price.recurring.interval}")
            else:
                print(f"    ${price.unit_amount / 100:.2f} (one-time)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Stripe products for Voice by Kraliki")
    parser.add_argument("--test", action="store_true", help="Use test mode (Stripe test keys)")
    parser.add_argument(
        "--list", action="store_true", help="List existing products instead of creating"
    )
    args = parser.parse_args()

    if args.list:
        list_products(test_mode=args.test)
    else:
        setup_stripe(test_mode=args.test)
