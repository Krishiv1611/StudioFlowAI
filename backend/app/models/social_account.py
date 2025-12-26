from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime, timezone
import enum


class SocialPlatform(enum.Enum):
    linkedin = "linkedin"
    twitter = "twitter"
    instagram = "instagram"
    google = "google"


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    platform = Column(
        Enum(SocialPlatform, name="social_platform_enum"),
        nullable=False
    )

    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)

    token_expires_at = Column(DateTime, nullable=True)

    profile_name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    user = relationship("app.models.user_model.User", back_populates="social_accounts")

