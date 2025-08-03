from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB  # Add this import
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class UserConnection(SQLModel, table=True):
    __tablename__ = "user_connections"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    url: str = Field(unique=True)
    first_name: str
    last_name: str
    company: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    connected_on: Optional[str] = None
    enriched: bool = False
    
    # Fix: Use Column with JSONB type instead of Field
    profile_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)  # Specify PostgreSQL JSONB type
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)