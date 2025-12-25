from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
    Enum
)
from app.config.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum


class ContentPlatform(enum.Enum):
    linkedin = "linkedin"
    twitter = "twitter"
    instagram = "instagram"


class ContentDraft(Base):
    __tablename__ = "content_drafts"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    status = Column(String, nullable=False)

    platform = Column(
        Enum(ContentPlatform, name="content_platform_enum"),
        nullable=False
    )

    content = Column(Text, nullable=False)
    
    scheduled_for = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    metrics = relationship(
        "PostMetrics",
        back_populates="content_draft"
    )
    
    project = relationship("app.models.project_model.Project", back_populates="content_drafts")
