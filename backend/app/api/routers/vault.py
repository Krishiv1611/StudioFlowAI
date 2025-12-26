from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user_model import User
from app.models.vault_model import KnowledgeVault
from app.services.rag_service import RagService
from pydantic import BaseModel

from app.schemas.vault_schema import VaultItem, SearchQuery

router = APIRouter(prefix="/vault", tags=["Knowledge Vault"])
rag_service = RagService() # Generic service

@router.post("/add")
def add_to_vault(
    item: VaultItem, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add content to the Knowledge Vault for RAG.
    """
    rag_service.store_content(db, current_user.id, item.content)
    return {"message": "Content added to vault."}
    
@router.get("/")
def list_vault(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all content chunks in the vault.
    """
    items = db.query(KnowledgeVault).filter(KnowledgeVault.user_id == current_user.id).all()
    # Exclude embedding from response for performance
    return [{"id": i.id, "content": i.content_chunk} for i in items]

@router.post("/search")
def search_vault(
    query: SearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform semantic search on the vault.
    """
    results = rag_service.search_vault(db, current_user.id, query.query, query.limit)
    return [{"content": r.content_chunk, "score": 0.0} for r in results] # Score depends on PGVector return
