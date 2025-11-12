"""seed default permissions

Revision ID: 36a93aaf3172
Revises: e2814b4f978b
Create Date: 2025-11-05 07:25:38.905913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36a93aaf3172'
down_revision: Union[str, None] = 'e2814b4f978b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from datetime import datetime, timezone
    import uuid
    
    permissions = [
        # Account Permissions
        {'id': str(uuid.uuid4()), 'name': 'accounts:create'},
        {'id': str(uuid.uuid4()), 'name': 'accounts:read'},
        {'id': str(uuid.uuid4()), 'name': 'accounts:update'},
        {'id': str(uuid.uuid4()), 'name': 'accounts:delete'},
        
        # Role Permissions
        {'id': str(uuid.uuid4()), 'name': 'roles:create'},
        {'id': str(uuid.uuid4()), 'name': 'roles:read'},
        {'id': str(uuid.uuid4()), 'name': 'roles:update'},
        {'id': str(uuid.uuid4()), 'name': 'roles:delete'},
        
        # Permission Permissions
        {'id': str(uuid.uuid4()), 'name': 'permissions:create'},
        {'id': str(uuid.uuid4()), 'name': 'permissions:read'},
        {'id': str(uuid.uuid4()), 'name': 'permissions:update'},
        {'id': str(uuid.uuid4()), 'name': 'permissions:delete'},
    ]
    
    # Insert permissions
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        sa.table('permissions',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        [
            {
                **perm,
                'created_at': now,
                'updated_at': now,
            }
            for perm in permissions
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissions WHERE name LIKE '%:%'")
