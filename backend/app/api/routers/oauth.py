from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_optional, get_current_user
from app.models.user_model import User
from app.models.social_account import SocialAccount, SocialPlatform
from app.config.settings import settings
from app.core.security import create_access_token, get_password_hash
from datetime import datetime, timezone
import uuid
import os
from requests_oauthlib import OAuth2Session

router = APIRouter(prefix="/auth/social", tags=["Social Auth"])

# --- Configuration Maps ---
OAUTH_CONFIG = {
    "google": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://accounts.google.com/o/oauth2/token",
        "scope": ["openid", "email", "profile"],
        "user_info_url": "https://www.googleapis.com/oauth2/v1/userinfo"
    },
    "linkedin": {
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scope": ["openid", "profile", "email"], # 'w_member_social' for posting if standard API
        "user_info_url": "https://api.linkedin.com/v2/userinfo"
    },
    # Twitter & Instagram can be complex. Assuming standard OAuth2 for this implementation.
    # Twitter often requires OAuth 2.0 with PKCE.
    "twitter": {
        "client_id": settings.TWITTER_CLIENT_ID,
        "client_secret": settings.TWITTER_CLIENT_SECRET,
        "authorize_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scope": ["users.read", "tweet.read", "tweet.write", "offline.access"],
        "user_info_url": "https://api.twitter.com/2/users/me"
    },
     "instagram": {
        "client_id": settings.INSTAGRAM_APP_ID,
        "client_secret": settings.INSTAGRAM_APP_SECRET,
        "authorize_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "scope": ["user_profile", "user_media"],
        "user_info_url": "https://graph.instagram.com/me" # requires fields param
    }
}

@router.get("/login/{platform}")
def login(platform: str):
    """
    Initiates the OAuth flow for Login or Linking.
    Redirect the user to the returned 'auth_url'.
    """
    if platform not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    
    config = OAUTH_CONFIG[platform]
    
    # Check if keys are configured (Development Safety)
    if not config["client_id"] or not config["client_secret"]:
         raise HTTPException(status_code=500, detail=f"Server configuration missing for {platform}")

    redirect_uri = f"http://localhost:8000/auth/social/callback/{platform}"
    
    oauth = OAuth2Session(
        client_id=config["client_id"], 
        redirect_uri=redirect_uri, 
        scope=config["scope"]
    )
    
    # For Twitter PKCE (if using requests-oauthlib with PKCE support, additional steps needed)
    # For simplicity, implementing standard Authorization Code Flow.
    
    authorization_url, state = oauth.authorization_url(config["authorize_url"])
    
    # In a real app, store 'state' in session/cookie to validate in callback
    return {"auth_url": authorization_url}

@router.get("/callback/{platform}")
def auth_callback(
    platform: str, 
    code: str, 
    state: str = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional) # Optional: might be anonymous login
):
    """
    Handles the OAuth callback.
    - If logged in -> Links account.
    - If anonymous -> Logs in (or creates user) via email matching.
    """
    if platform not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported platform")
        
    config = OAUTH_CONFIG[platform]
    redirect_uri = f"http://localhost:8000/auth/social/callback/{platform}"
    
    try:
        oauth = OAuth2Session(
            client_id=config["client_id"], 
            redirect_uri=redirect_uri
        )
        
        # 1. Fetch Token
        token = oauth.fetch_token(
            token_url=config["token_url"],
            client_secret=config["client_secret"],
            code=code
        )
        
        # 2. Fetch User Info
        # Note: Each provider has different response structures. 
        # Standardizing logic here for briefness.
        
        user_info = {}
        if platform == "google" or platform == "linkedin":
             resp = oauth.get(config["user_info_url"])
             user_info = resp.json() 
             # Google: {email, name, sub, picture}
             # LinkedIn: {email, name, sub, picture} (if openid used)
             
        elif platform == "twitter":
             resp = oauth.get(config["user_info_url"])
             data = resp.json().get("data", {})
             user_info = {"sub": data.get("id"), "name": data.get("name"), "username": data.get("username")}
             
        elif platform == "instagram":
             # Instagram Basic Display
             resp = oauth.get(config["user_info_url"] + "?fields=id,username")
             user_info = resp.json()
             user_info["sub"] = user_info.get("id")
             user_info["name"] = user_info.get("username")

        # Extract common fields
        social_id = str(user_info.get("sub", user_info.get("id")))
        email = user_info.get("email") # Only reliably present for Google/LinkedIn
        name = user_info.get("name", "Social User")
        
        # 3. Logic: Link or Login?
        
        # A. If User is already authenticated (Linking Flow)
        if current_user:
            # Check if linked
            existing = db.query(SocialAccount).filter(
                SocialAccount.user_id == current_user.id,
                SocialAccount.platform == platform
            ).first()
            
            if existing: # Update
                existing.access_token = token.get("access_token")
                existing.refresh_token = token.get("refresh_token")
                db.commit()
                return {"message": f"Updated link for {platform}", "account_id": existing.id}
            else: # Create
                new_account = SocialAccount(
                    user_id=current_user.id,
                    platform=platform,
                    access_token=token.get("access_token"),
                    refresh_token=token.get("refresh_token"),
                    profile_name=name,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_account)
                db.commit()
                return {"message": f"Successfully linked {platform}", "account_id": new_account.id}
                
        # B. Anonymous -> Login Flow
        else:
            if not email and platform == "google": 
                raise HTTPException(status_code=400, detail="Email not provided by social provider")
            
            # 1. Check if SocialAccount exists (Login via Social ID)
            # Find User via SocialAccount joined
            # (Requires loop or join query)
            
            # Simplifying: Check if user exists by Email (if email provided)
            target_user = None
            if email:
                target_user = db.query(User).filter(User.email == email).first()
                
            if not target_user:
                # Create New User
                # Random password
                pwd_string = uuid.uuid4().hex
                target_user = User(
                    email=email if email else f"{social_id}@{platform}.com", # Fallback email
                    full_name=name,
                    hashed_password=get_password_hash(pwd_string),
                    brand_voice_style="Professional"
                )
                db.add(target_user)
                db.commit()
                db.refresh(target_user)
                
            # Ensure Social Link exists
            link = db.query(SocialAccount).filter(SocialAccount.user_id==target_user.id, SocialAccount.platform==platform).first()
            if not link:
                 link = SocialAccount(
                    user_id=target_user.id,
                    platform=platform,
                    access_token=token.get("access_token"),
                    refresh_token=token.get("refresh_token"),
                    profile_name=name,
                    created_at=datetime.now(timezone.utc)
                )
                 db.add(link)
                 db.commit()
            
            # Issue JWT
            access_token = create_access_token(subject=target_user.email)
            return {"access_token": access_token, "token_type": "bearer", "login_via": platform}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth Error: {str(e)}")

@router.get("/accounts")
def list_linked_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Must be auth
):
    """
    List all linked social accounts for the user.
    """
    accounts = db.query(SocialAccount).filter(SocialAccount.user_id == current_user.id).all()
    # Mask tokens for security
    return [{
        "platform": a.platform, 
        "profile_name": a.profile_name, 
        "connected_at": a.created_at
    } for a in accounts]
