from sqlalchemy import Column, String, Boolean, DateTime, LargeBinary, func
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=func.gen_random_uuid())
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(10), default="USER")
    api_key_encrypted = Column(LargeBinary)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())
