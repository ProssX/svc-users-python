"""seed default roles

Revision ID: f37cde5070f0
Revises: 36a93aaf3172
Create Date: 2025-11-05 07:25:47.470298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f37cde5070f0'
down_revision: Union[str, None] = '36a93aaf3172'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from datetime import datetime, timezone
    import uuid
    
    # Generate role IDs
    admin_id = str(uuid.uuid4())
    manager_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create roles
    now = datetime.now(timezone.utc)
    roles = [
        {
            'id': admin_id,
            'name': 'Admin',
            'description': 'Full system access with all permissions',
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': manager_id,
            'name': 'Manager',
            'description': 'Read and update permissions for accounts and roles',
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': user_id,
            'name': 'User',
            'description': 'Basic read access to own account',
            'created_at': now,
            'updated_at': now,
        },
    ]
    
    op.bulk_insert(
        sa.table('roles',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        roles
    )
    
    # Get permission IDs by name
    from sqlalchemy import select
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id, name FROM permissions"))
    perm_map = {row[1]: row[0] for row in result}
    
    # Assign permissions to roles
    role_permissions = [
        # Admin - ALL permissions
        {'role_id': admin_id, 'permission_id': perm_map['accounts:create']},
        {'role_id': admin_id, 'permission_id': perm_map['accounts:read']},
        {'role_id': admin_id, 'permission_id': perm_map['accounts:update']},
        {'role_id': admin_id, 'permission_id': perm_map['accounts:delete']},
        {'role_id': admin_id, 'permission_id': perm_map['roles:create']},
        {'role_id': admin_id, 'permission_id': perm_map['roles:read']},
        {'role_id': admin_id, 'permission_id': perm_map['roles:update']},
        {'role_id': admin_id, 'permission_id': perm_map['roles:delete']},
        {'role_id': admin_id, 'permission_id': perm_map['permissions:create']},
        {'role_id': admin_id, 'permission_id': perm_map['permissions:read']},
        {'role_id': admin_id, 'permission_id': perm_map['permissions:update']},
        {'role_id': admin_id, 'permission_id': perm_map['permissions:delete']},
        
        # Manager - Read and Update for accounts/roles
        {'role_id': manager_id, 'permission_id': perm_map['accounts:read']},
        {'role_id': manager_id, 'permission_id': perm_map['accounts:update']},
        {'role_id': manager_id, 'permission_id': perm_map['roles:read']},
        {'role_id': manager_id, 'permission_id': perm_map['permissions:read']},
        
        # User - Only read own account
        {'role_id': user_id, 'permission_id': perm_map['accounts:read']},
    ]
    
    op.bulk_insert(
        sa.table('role_permissions',
            sa.column('role_id', sa.String),
            sa.column('permission_id', sa.String),
        ),
        role_permissions
    )


def downgrade() -> None:
    # Delete role_permissions first (foreign key)
    op.execute("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE name IN ('Admin', 'Manager', 'User'))")
    
    # Delete roles
    op.execute("DELETE FROM roles WHERE name IN ('Admin', 'Manager', 'User')")
