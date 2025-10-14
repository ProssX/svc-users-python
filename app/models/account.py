"""
Account model.
Represents a user account with email/password authentication.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    """Account model - represents a user with email/password and role."""
    
    __tablename__ = "accounts"
    
    # Primary key - using email as PK
    email = Column(String(255), primary_key=True, nullable=False)
    
    # Fields
    password_hash = Column(String(255), nullable=False)
    
    # Foreign key
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="accounts")
    
    def __repr__(self):
        return f"<Account(email='{self.email}')>"
