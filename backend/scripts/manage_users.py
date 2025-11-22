#!/usr/bin/env python3
"""
User management script for The AI Exchange.
Allows promoting users to ADMIN role without needing database edits.

Usage:
    python manage_users.py promote-admin <email>   # Promote user to ADMIN
    python manage_users.py list-users              # Show all users and roles
    python manage_users.py create-admin <email> <name> <password>  # Create new admin
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import User, UserRole
from app.services.database import engine


def list_users():
    """List all users with their roles."""
    session = Session(engine)
    try:
        users = session.exec(select(User)).all()

        if not users:
            print("❌ No users found in database")
            return

        print("\n📋 Users in Database:")
        print("-" * 70)
        print(f"{'Email':<35} {'Name':<25} {'Role':<10}")
        print("-" * 70)

        for user in sorted(users, key=lambda u: u.email):
            print(f"{user.email:<35} {user.full_name:<25} {user.role.value:<10}")

        print("-" * 70)
        admin_count = len([u for u in users if u.role == UserRole.ADMIN])
        staff_count = len([u for u in users if u.role == UserRole.STAFF])
        print(f"\nTotal: {len(users)} users ({admin_count} ADMIN, {staff_count} STAFF)")

    finally:
        session.close()


def promote_to_admin(email: str):
    """Promote a user to ADMIN role."""
    session = Session(engine)
    try:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            print(f"❌ User not found: {email}")
            return False

        if user.role == UserRole.ADMIN:
            print(f"⚠️  {email} is already an ADMIN")
            return False

        user.role = UserRole.ADMIN
        session.add(user)
        session.commit()

        print(f"✅ Promoted {email} ({user.full_name}) to ADMIN")
        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        session.close()


def create_admin(email: str, full_name: str, password: str):
    """Create a new ADMIN user."""
    session = Session(engine)
    try:
        # Check if user exists
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print(f"❌ User already exists: {email}")
            return False

        # Create new admin user
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True,
        )

        session.add(user)
        session.commit()

        print(f"✅ Created ADMIN account: {email}")
        print(f"   Name: {full_name}")
        print(f"   Password: {password}")
        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        session.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "list-users":
        list_users()
    elif command == "promote-admin":
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py promote-admin <email>")
            sys.exit(1)
        email = sys.argv[2]
        success = promote_to_admin(email)
        sys.exit(0 if success else 1)
    elif command == "create-admin":
        if len(sys.argv) < 5:
            print("❌ Usage: python manage_users.py create-admin <email> <name> <password>")
            sys.exit(1)
        email = sys.argv[2]
        name = sys.argv[3]
        password = sys.argv[4]
        success = create_admin(email, name, password)
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
