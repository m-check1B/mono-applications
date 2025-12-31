#!/usr/bin/env python3
"""
Create developer accounts for accelerator team.

Usage:
    python3 scripts/create-dev-accounts.py dev1@example.com "Dev One"
    python3 scripts/create-dev-accounts.py --bulk devs.csv

CSV format:
    email,name
    dev1@example.com,Dev One
    dev2@example.com,Dev Two
"""

import sys
import os
import csv
import secrets
import string

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.security_v2 import get_password_hash, generate_id
from app.models.user import User, Role
from app.services.knowledge_defaults import ensure_default_item_types
from app.services.workspace_service import WorkspaceService


def generate_temp_password(length=16):
    """Generate a secure temporary password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_dev_account(db, email: str, name: str) -> tuple[User, str]:
    """Create a developer account with SUPERVISOR role."""

    # Check if exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"  User {email} already exists, updating role to SUPERVISOR")
        existing.role = Role.SUPERVISOR
        db.commit()
        return existing, None

    # Generate temp password
    temp_password = generate_temp_password()

    # Parse name
    parts = name.split() if name else ["Developer"]
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    user = User(
        id=generate_id(),
        email=email,
        username=name,
        firstName=first_name,
        lastName=last_name,
        passwordHash=get_password_hash(temp_password),
        organizationId=generate_id(),
        role=Role.SUPERVISOR,  # Dev tier
        onboardingCompleted=False,
        featureToggles={
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True,
        },
        privacyPreferences={
            "geminiFileSearchEnabled": True,
            "iiAgentEnabled": True,
            "dataPrivacyAcknowledged": False,
        },
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize defaults
    ensure_default_item_types(user.id, db)
    WorkspaceService.ensure_default_workspace(user, db)

    return user, temp_password


def main():
    # Load database URL
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set in backend/.env")
        sys.exit(1)

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        if len(sys.argv) < 2:
            print(__doc__)
            sys.exit(1)

        accounts = []

        if sys.argv[1] == '--bulk':
            # Bulk create from CSV
            csv_path = sys.argv[2]
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    accounts.append((row['email'], row['name']))
        else:
            # Single account
            email = sys.argv[1]
            name = sys.argv[2] if len(sys.argv) > 2 else email.split('@')[0]
            accounts.append((email, name))

        print(f"\nCreating {len(accounts)} developer account(s)...\n")
        print("-" * 60)

        created = []
        for email, name in accounts:
            print(f"Creating: {email} ({name})")
            user, temp_password = create_dev_account(db, email, name)
            if temp_password:
                created.append((email, temp_password))
                print(f"  Created with role: SUPERVISOR (Dev tier)")
            print()

        print("-" * 60)
        print("\nACCOUNTS CREATED:")
        print("-" * 60)

        for email, password in created:
            print(f"Email:    {email}")
            print(f"Password: {password}")
            print(f"Role:     SUPERVISOR (Dev tier)")
            print(f"Login:    https://focus.verduona.dev/login")
            print("-" * 60)

        print("\nDone! Devs should change their password after first login.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
