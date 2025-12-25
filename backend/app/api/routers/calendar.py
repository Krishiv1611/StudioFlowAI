from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user_model import User
from app.models.content_draft import ContentDraft
from app.models.project_model import Project

router = APIRouter(prefix="/calendar", tags=["Smart Calendar"])

@router.get("/events")
def get_calendar_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all scheduled posts formatted for a Calendar View.
    """
    # Fetch all drafts with a scheduled_for date
    drafts = db.query(ContentDraft).join(Project).filter(
        Project.user_id == current_user.id,
        ContentDraft.scheduled_for.isnot(None)
    ).all()
    
    events = []
    for d in drafts:
        events.append({
            "id": d.id,
            "title": f"{d.platform.value.capitalize()} Post: {d.content[:30]}...",
            "start": d.scheduled_for,
            "status": d.status,
            "extendedProps": {
                "platform": d.platform.value,
                "full_content": d.content
            }
        })
        
    return events
