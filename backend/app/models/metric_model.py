from sqlalchemy import Column, Integer, String, Text, DateTime
from app.config.database import Base
from datetime import datetime, timezone

class PostMetrics(Base):
    __tablename__ = "post_metrics"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("content_drafts.id"), nullable=False)
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )