"""seed complete permissions and roles

Revision ID: a1b2c3d4e5f6
Revises: f37cde5070f0
Create Date: 2025-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f37cde5070f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Seeds all permissions and creates Organization Administrator role.
    This migration is idempotent - it will not create duplicates.
    """
    from datetime import datetime, timezone
    import uuid
    
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    
    # Define all permissions
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
    
    # Insert permissions (only if they don't exist)
    permission_ids = {}
    for perm_name in permission_names:
        # Check if permission exists
        result = conn.execute(
            sa.text("SELECT id FROM permissions WHERE name = :name"),
            {"name": perm_name}
        )
        existing = result.fetchone()
        
        if existing:
            permission_ids[perm_name] = existing[0]
        else:
            # Create new permission
            perm_id = str(uuid.uuid4())
            conn.execute(
                sa.text("""
                    INSERT INTO permissions (id, name, created_at, updated_at)
                    VALUES (:id, :name, :created_at, :updated_at)
                """),
                {
                    "id": perm_id,
                    "name": perm_name,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            permission_ids[perm_name] = perm_id
    
    # Create Organization Administrator role (if it doesn't exist)
    result = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = :name"),
        {"name": "Organization Administrator"}
    )
    existing_role = result.fetchone()
    
    if not existing_role:
        org_admin_id = str(uuid.uuid4())
        conn.execute(
            sa.text("""
                INSERT INTO roles (id, name, description, created_at, updated_at)
                VALUES (:id, :name, :description, :created_at, :updated_at)
            """),
            {
                "id": org_admin_id,
                "name": "Organization Administrator",
                "description": "Full organizational access with all permissions",
                "created_at": now,
                "updated_at": now,
            }
        )
        
        # Assign all permissions to Organization Administrator role
        for perm_id in permission_ids.values():
            conn.execute(
                sa.text("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                """),
                {
                    "role_id": org_admin_id,
                    "permission_id": perm_id,
                }
            )
    else:
        # Role exists, ensure it has all permissions
        org_admin_id = existing_role[0]
        
        # Get existing permission assignments
        result = conn.execute(
            sa.text("SELECT permission_id FROM role_permissions WHERE role_id = :role_id"),
            {"role_id": org_admin_id}
        )
        existing_perms = {row[0] for row in result}
        
        # Add missing permissions
        for perm_id in permission_ids.values():
            if perm_id not in existing_perms:
                conn.execute(
                    sa.text("""
                        INSERT INTO role_permissions (role_id, permission_id)
                        VALUES (:role_id, :permission_id)
                    """),
                    {
                        "role_id": org_admin_id,
                        "permission_id": perm_id,
                    }
                )


def downgrade() -> None:
    """
    Remove Organization Administrator role and newly added permissions.
    Note: This only removes permissions that are not used by other roles.
    """
    conn = op.get_bind()
    
    # Remove Organization Administrator role
    conn.execute(
        sa.text("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE name = 'Organization Administrator')")
    )
    conn.execute(
        sa.text("DELETE FROM roles WHERE name = 'Organization Administrator'")
    )
    
    # Remove new permissions (organization, employee, process, interview)
    new_permission_patterns = [
        'organization:%',
        'organizations:%',
        'employee:%',
        'process:%',
        'interviews:%',
    ]
    
    for pattern in new_permission_patterns:
        conn.execute(
            sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE name LIKE :pattern)"),
            {"pattern": pattern}
        )
        conn.execute(
            sa.text("DELETE FROM permissions WHERE name LIKE :pattern"),
            {"pattern": pattern}
        )
