"""Initialize database and create first admin user."""

import sys
from uuid import uuid4

from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.core.security import hash_password
from app.models import User, UserRole
from app.services.database import engine


def init_db() -> None:
    """Create database tables and first admin user."""
    print("Initializing database...")

    # Create tables
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created/verified")

    # Check if admin user exists
    with Session(engine) as session:
        admin = session.exec(
            select(User).where(User.role == UserRole.ADMIN)
        ).first()

        if admin:
            print("✓ Admin user already exists")
            return

        # Create first admin user
        print("\n" + "=" * 60)
        print("Creating first admin user")
        print("=" * 60)

        while True:
            email = input("Enter admin email: ").strip()
            if "@curtin.edu.au" not in email:
                print("⚠ Warning: Email is not @curtin.edu.au domain")
            if email:
                break

        while True:
            full_name = input("Enter admin full name: ").strip()
            if full_name:
                break

        while True:
            password = input("Enter admin password (min 8 chars): ").strip()
            if len(password) >= 8:
                break
            print("⚠ Password must be at least 8 characters")

        # Create admin user
        admin_user = User(
            id=uuid4(),
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True,
        )

        session.add(admin_user)
        session.commit()

        print(f"\n✓ Admin user created successfully!")
        print(f"  Email: {admin_user.email}")
        print(f"  Name: {admin_user.full_name}")
        print(f"  Role: {admin_user.role.value}")
        print("\nYou can now log in with these credentials.")


if __name__ == "__main__":
    try:
        init_db()
        print("\n✓ Database initialization complete!")
    except KeyboardInterrupt:
        print("\n\n⚠ Database initialization cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during database initialization: {e}")
        sys.exit(1)
