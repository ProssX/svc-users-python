"""
Database seeding script.
Initializes the database with default roles and permissions.
"""
import sys
import uuid
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, init_db
from app.models import Permission, Role, Account
from app.services.auth_service import hash_password

# Default organization ID for seed accounts
DEFAULT_ORG_ID = uuid.uuid4()


def seed_permissions(db: Session):
    """Create default permissions."""
    print("Creating permissions...")
    
    permission_names = [
        "accounts:create",
        "accounts:read",
        "accounts:update",
        "accounts:delete",
        "roles:create",
        "roles:read",
        "roles:update",
        "roles:delete",
        "permissions:create",
        "permissions:read",
        "permissions:update",
        "permissions:delete",
    ]
    
    permissions = []
    for name in permission_names:
        # Check if permission already exists
        existing = db.query(Permission).filter(Permission.name == name).first()
        if not existing:
            permission = Permission(name=name)
            db.add(permission)
            permissions.append(permission)
            print(f"  ✓ Created permission: {name}")
        else:
            permissions.append(existing)
            print(f"  → Permission already exists: {name}")
    
    db.commit()
    return permissions


def seed_roles(db: Session, permissions):
    """Create default roles and assign permissions."""
    print("\nCreating roles...")
    
    # Admin role - all permissions
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        admin_role = Role(
            name="Admin",
            description="Full system access with all permissions"
        )
        admin_role.permissions = permissions
        db.add(admin_role)
        db.commit()
        print(f"  ✓ Created role: Admin (with {len(permissions)} permissions)")
    else:
        print("  → Role already exists: Admin")
    
    # Manager role - accounts and roles read/update
    manager_role = db.query(Role).filter(Role.name == "Manager").first()
    if not manager_role:
        manager_permissions = [p for p in permissions if 
                              p.name in ["accounts:read", "accounts:update", 
                                        "roles:read", "permissions:read"]]
        manager_role = Role(
            name="Manager",
            description="Team management access"
        )
        manager_role.permissions = manager_permissions
        db.add(manager_role)
        db.commit()
        print(f"  ✓ Created role: Manager (with {len(manager_permissions)} permissions)")
    else:
        print("  → Role already exists: Manager")
    
    # User role - basic read access
    user_role = db.query(Role).filter(Role.name == "User").first()
    if not user_role:
        user_permissions = [p for p in permissions if p.name == "accounts:read"]
        user_role = Role(
            name="User",
            description="Basic user access"
        )
        user_role.permissions = user_permissions
        db.add(user_role)
        db.commit()
        print(f"  ✓ Created role: User (with {len(user_permissions)} permissions)")
    else:
        print("  → Role already exists: User")
    
    return admin_role, manager_role, user_role


def seed_accounts(db: Session, admin_role, user_role):
    """Create sample accounts (optional)."""
    print("\nCreating sample accounts...")
    
    # Admin account
    admin_email = "admin@example.com"
    admin_account = db.query(Account).filter(Account.email == admin_email).first()
    if not admin_account:
        admin_account = Account(
            email=admin_email,
            password_hash=hash_password("admin123"),  # Change this in production!
            role_id=admin_role.id,
            organization_id=DEFAULT_ORG_ID
        )
        db.add(admin_account)
        db.commit()
        print(f"  ✓ Created account: {admin_email} (password: admin123)")
    else:
        print(f"  → Account already exists: {admin_email}")
    
    # Regular user account
    user_email = "user@example.com"
    user_account = db.query(Account).filter(Account.email == user_email).first()
    if not user_account:
        user_account = Account(
            email=user_email,
            password_hash=hash_password("user123"),  # Change this in production!
            role_id=user_role.id,
            organization_id=DEFAULT_ORG_ID
        )
        db.add(user_account)
        db.commit()
        print(f"  ✓ Created account: {user_email} (password: user123)")
    else:
        print(f"  → Account already exists: {user_email}")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)
    
    try:
        # Initialize database (create tables)
        print("\nInitializing database tables...")
        init_db()
        print("  ✓ Database tables created")
        
        # Create database session
        db = SessionLocal()
        
        # Seed data
        permissions = seed_permissions(db)
        admin_role, manager_role, user_role = seed_roles(db, permissions)
        seed_accounts(db, admin_role, user_role)
        
        # Close session
        db.close()
        
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print("\nSample accounts created:")
        print("  - admin@example.com / admin123 (Admin role)")
        print("  - user@example.com / user123 (User role)")
        print("\n⚠️  Remember to change these passwords in production!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
