from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user_model import User
from app.models.social_account import SocialAccount, SocialPlatform
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/auth/social", tags=["Social Auth"])

@router.get("/link/{platform}", status_code=status.HTTP_200_OK)
def get_auth_url(platform: str, current_user: User = Depends(get_current_user)):
    """
    Returns the OAuth authorization URL for the specified platform.
    (Mocked for this product version as we lack real Client IDs)
    """
    if platform not in SocialPlatform._member_names_:
        raise HTTPException(status_code=400, detail="Unsupported platform")
        
    # In a real app, this would use the platform's SDK to generate a Redirect URL.
    # For now, we return a mock URL that would redirect back to our callback.
    mock_auth_url = f"https://mock-{platform}.com/oauth/authorize?client_id=MY_APP&redirect_uri=http://localhost:8000/auth/social/callback/{platform}&state={current_user.id}"
    
    return {"auth_url": mock_auth_url}

@router.get("/callback/{platform}")
def auth_callback(
    platform: str, 
    code: str = "mock_code", 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Callback endpoint that receives the auth code and exchanges it for a token.
    (Mocked to instantly link the account)
    """
    if platform not in SocialPlatform._member_names_:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    
    # Check if already linked
    existing = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == platform
    ).first()
    
    if existing:
        # Update token
        existing.access_token = f"mock_access_token_{uuid.uuid4().hex}"
        existing.status = "active"
        db.commit()
        return {"message": f"Updated link for {platform}", "account_id": existing.id}
    
    # Create new link
    new_account = SocialAccount(
        user_id=current_user.id,
        platform=platform,
        access_token=f"mock_access_token_{uuid.uuid4().hex}",
        refresh_token=f"mock_refresh_token_{uuid.uuid4().hex}",
        profile_name=f"{current_user.full_name}'s {platform}", # Mock profile name
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return {"message": f"Successfully linked {platform}", "account_id": new_account.id}

@router.get("/accounts")
def list_linked_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all linked social accounts for the user.
    """
    accounts = db.query(SocialAccount).filter(SocialAccount.user_id == current_user.id).all()
    return accounts
