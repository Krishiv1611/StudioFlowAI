from sqlalchemy import Column, Integer, String, Text, DateTime
from app.config.database import Base
from datetime import datetime, timezone


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True, index=True)

    agent_name = Column(String, nullable=False)
    step_summary = Column(String, nullable=False)

    full_output = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

