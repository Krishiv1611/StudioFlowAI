from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user_model import User
from app.models.content_draft import ContentDraft
from app.models.project_model import Project

router = APIRouter(prefix="/posts", tags=["Posts & Drafts"])

from app.models.content_draft import ContentPlatform
class PostCreate(BaseModel):
    content: str
    platform: str = "twitter"
    scheduled_for: Optional[datetime] = None

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post_manually(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually create a content draft (bypassing AI).
    """
    # Get/Create General Project
    project = db.query(Project).filter(Project.user_id == current_user.id, Project.name == "General").first()
    if not project:
        project = Project(user_id=current_user.id, name="General", description="Default project", status="active")
        db.add(project)
        db.commit()
        db.refresh(project)
        
    plat_enum = ContentPlatform.twitter
    if post_in.platform.lower() == "linkedin": plat_enum = ContentPlatform.linkedin
    if post_in.platform.lower() == "instagram": plat_enum = ContentPlatform.instagram
    
    new_draft = ContentDraft(
        project_id=project.id,
        status="draft",
        platform=plat_enum,
        content=post_in.content,
        scheduled_for=post_in.scheduled_for
    )
    db.add(new_draft)
    db.commit()
    db.refresh(new_draft)
    return new_draft

@router.get("/")
def list_posts(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all content drafts/posts across all projects.
    Optional filter: ?status=pending_approval | published | rejected
    """
    query = db.query(ContentDraft).join(Project).filter(Project.user_id == current_user.id)
    
    if status:
        query = query.filter(ContentDraft.status == status)
        
    posts = query.all()
    return posts

@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(ContentDraft).join(Project).filter(
        Project.user_id == current_user.id,
        ContentDraft.id == post_id
    ).first()
    
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import Response, status

class PostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None

@router.patch("/{post_id}")
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a post/draft. 
    Use this to reschedule (update scheduled_for) or edit content.
    """
    post = db.query(ContentDraft).join(Project).filter(
        Project.user_id == current_user.id,
        ContentDraft.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if post_update.content is not None:
        post.content = post_update.content
    if post_update.status is not None:
        post.status = post_update.status
    if post_update.scheduled_for is not None:
        post.scheduled_for = post_update.scheduled_for
        
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a post/draft.
    """
    post = db.query(ContentDraft).join(Project).filter(
        Project.user_id == current_user.id,
        ContentDraft.id == post_id
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
