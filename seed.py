"""
Database seeding script.
Initializes the database with default roles and permissions.
"""
import sys
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, init_db
from app.models import Permission, Role


def seed_permissions(db: Session):
    """Create default permissions."""
    print("Creating permissions...")
    
    permission_names = [
        # Auth permissions
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
        # Organization permissions
        "organization:read",
        "organizations:read",
        "organizations:create",
        "organizations:delete",
        "organizations:update",
        # Employee permissions
        "employee:create",
        "employee:write",
        "employee:update",
        "employee:read",
        "employee:delete",
        # Process permissions
        "process:read",
        "process:create",
        "process:delete",
        "process:update",
        # Interview permissions
        "interviews:create",
        "interviews:read",
        "interviews:read_all",
        "interviews:update",
        "interviews:delete",
        "interviews:export",
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
    """Create Organization Administrator role and assign all permissions."""
    print("\nCreating roles...")
    
    # Organization Administrator role - all permissions
    org_admin_role = db.query(Role).filter(Role.name == "Organization Administrator").first()
    if not org_admin_role:
        org_admin_role = Role(
            name="Organization Administrator",
            description="Full organizational access with all permissions"
        )
        org_admin_role.permissions = permissions
        db.add(org_admin_role)
        db.commit()
        print(f"  ✓ Created role: Organization Administrator (with {len(permissions)} permissions)")
    else:
        print("  → Role already exists: Organization Administrator")
    
    return org_admin_role


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
        org_admin_role = seed_roles(db, permissions)
        
        # Close session
        db.close()
        
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print("\nCreated:")
        print(f"  - {len(permissions)} permissions")
        print("  - Organization Administrator role with all permissions")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
