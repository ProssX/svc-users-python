"""
Database seeding script for test accounts.
Run after migrations: python -m app.scripts.seed

This script only creates test accounts for development.
Permissions and roles are managed by Alembic migrations.
"""
import sys
import uuid
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Role, Account
from app.services.auth_service import hash_password

# Default organization ID for seed accounts
DEFAULT_ORG_ID = uuid.uuid4()


def seed_test_accounts(db: Session):
    """Create test accounts for development."""
    print("\n" + "=" * 70)
    print("Creating test accounts for development...")
    print("=" * 70)
    
    # Get roles (already created by migrations)
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    user_role = db.query(Role).filter(Role.name == "User").first()
    
    if not admin_role or not user_role:
        print("\n✗ Error: Roles not found in database.")
        print("  Make sure you've run migrations first:")
        print("  → alembic upgrade head")
        print("=" * 70 + "\n")
        sys.exit(1)
    
    # Admin account
    admin_email = "admin@example.com"
    admin_account = db.query(Account).filter(Account.email == admin_email).first()
    if not admin_account:
        admin_account = Account(
            email=admin_email,
            password_hash=hash_password("admin123"),
            role_id=admin_role.id,
            entity_id=DEFAULT_ORG_ID,
            organization_id=DEFAULT_ORG_ID
        )
        db.add(admin_account)
        print(f"\n  ✓ Created: {admin_email}")
        print(f"    Password: admin123")
        print(f"    Role: Admin")
    else:
        print(f"\n  → Already exists: {admin_email}")
    
    # User account
    user_email = "user@example.com"
    user_account = db.query(Account).filter(Account.email == user_email).first()
    if not user_account:
        user_account = Account(
            email=user_email,
            password_hash=hash_password("user123"),
            role_id=user_role.id,
            entity_id=DEFAULT_ORG_ID,
            organization_id=DEFAULT_ORG_ID
        )
        db.add(user_account)
        print(f"\n  ✓ Created: {user_email}")
        print(f"    Password: user123")
        print(f"    Role: User")
    else:
        print(f"\n  → Already exists: {user_email}")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print("✓ Test accounts ready!")
    print("=" * 70)
    print("\nDefault test accounts:")
    print("  • admin@example.com / admin123 (Admin role)")
    print("  • user@example.com / user123 (User role)")
    print("\n⚠️  WARNING: For development only!")
    print("   Change these passwords before deploying to production.")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    try:
        db = SessionLocal()
        seed_test_accounts(db)
        db.close()
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        print("=" * 70 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
