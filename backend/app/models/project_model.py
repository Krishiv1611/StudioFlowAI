from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.config.database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    content_drafts=relationship("ContentDraft",back_populates="project")
    user = relationship("app.models.user_model.User", back_populates="projects")