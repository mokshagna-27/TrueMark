
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.api.core.database import Base


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), nullable=False, index=True)
    document_title = Column(String(255), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    note = Column(Text, nullable=False, default="Content updated")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
