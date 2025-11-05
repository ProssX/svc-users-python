"""
Account model.
Represents a user account with email/password authentication.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    """Account model - represents a user with email/password and role."""
    
    __tablename__ = "accounts"
    
    # Primary key - using email as PK
    email = Column(String(255), primary_key=True, nullable=False)

    # Entity identifier (UUID) - separate from PK, auto-generated
    entity_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, index=True)

    # Organization identifier (UUID) - links account to an organization
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Fields
    password_hash = Column(String(255), nullable=False)
    
    # Foreign key
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="accounts")
    
    def __repr__(self):
        return f"<Account(email='{self.email}', entity_id='{self.entity_id}')>"
