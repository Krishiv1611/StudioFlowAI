from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    content: str
    platform: str = "twitter"
    scheduled_for: Optional[datetime] = None

class PostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None
