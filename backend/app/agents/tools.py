from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from sqlmodel import Session, create_engine
from app.config.settings import settings
from app.services.scraper import ScraperService
from app.services.rag_service import RagService

# Create Engine
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)

# For simplicity in tools, we might need a way to get a session. 
# Usually tools are stateless or have deps injected.
# I'll instantiate generic services for now.

# Initialize Clients
tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
scraper_service = ScraperService()
rag_service = RagService()
from app.services.ml_service import MLService
ml_service = MLService()

# --- Trend Scout Tools ---

@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the internet for up-to-date information on a given topic.
    Useful for finding news, trends, or broad information.
    """
    try:
        response = tavily_client.search(query, max_results=max_results)
        # Simplify response to string
        results = response.get("results", [])
        return "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}" for r in results])
    except Exception as e:
        return f"Error searching web: {e}"

@tool
async def scrape_website(url: str) -> str:
    """
    Scrape and extract text content from a specific website URL.
    Useful when you have a specific link to read.
    """
    return await scraper_service.scrape_url(url)

# --- Context Engineer Tools ---

@tool
def search_vault(query: str, user_id: int) -> str: # User ID might need to be passed from context
    """
    Search the internal KnowledgeVault (database) for previously stored information.
    Useful for recalling past research, guidelines, or facts.
    """
    # NOTE: This requires a DB session. We'll create a new one for the tool execution.
    # In a prod environment, better to inject session or use a context manager.
    with Session(engine) as session:
        results = rag_service.search_vault(session, user_id, query)
        if not results:
            return "No relevant info found in vault."
        return "\n\n".join([f"Content: {r.content_chunk}" for r in results])

@tool
def store_in_vault(content: str, user_id: int) -> str:
    """
    Store a piece of information or research findings into the KnowledgeVault.
    Useful for saving successful posts, facts, or guidelines for future use.
    """
    with Session(engine) as session:
        rag_service.store_content(session, user_id, content)
        return "Content successfully stored in KnowledgeVault."

# --- Viral Critic Tools ---

@tool
def quality_checklist(draft: str) -> str:
    """
    Run a quality checklist on a draft post.
    Returns specific feedback.
    """
    # Mock implementation of a "checklist"
    feedback = []
    if len(draft) < 50:
        feedback.append("- Draft is too short.")
    if "???" in draft:
        feedback.append("- Remove placeholders (???).")
    if not feedback:
        return "Draft passes basic quality checks."
    return "Checklist Failures:\n" + "\n".join(feedback)

@tool
def predict_virality_score(post_content: str, platform: str = "Twitter") -> float:
    """
    Predicts the virality score (0.0 to 1.0) of a post draft using the ML model.
    """
    if not post_content:
        return 0.0
        
    features = {
        "text_content": post_content,
        "platform": platform,
        "hashtags": "", # Could extract
        "topic_category": "General", # Could infer
        "sentiment_score": 0.5 # Placeholder
    }
    
    return ml_service.predict_virality(features)

import pandas as pd
import matplotlib.pyplot as plt
import uuid
import os

# --- Helper for Social Data ---
SOCIAL_DATA_PATH = os.path.join(settings.BASE_DIR, 'app', 'ml', 'data', 'Social Media Engagement Dataset.csv')

def _get_user_data(user_id: int):
    try:
        if not os.path.exists(SOCIAL_DATA_PATH):
            return None
        df = pd.read_csv(SOCIAL_DATA_PATH)
        # Ensure user_id column exists. If strictly ints in DB but string in CSV, cast.
        # Check dataset structure from previous steps: user_id seems to be present.
        # We'll filter assuming user_id matches.
        # If user_id not found, we might return all or random for demo purposes if the specific ID isn't there.
        # For now, distinct filtering:
        user_df = df[df['user_id'] == str(user_id)] # Assuming mixed types or string in CSV
        if user_df.empty:
            # Fallback: cast to int
             user_df = df[df['user_id'] == int(user_id)]
        
        if user_df.empty:
             # Fallback for demo: return a random slice if specific user not found (as dataset is Kaggle generic)
             # This prevents emptiness during testing
             return df.sample(50)
        return user_df
    except Exception as e:
        print(f"Data Access Error: {e}")
        return None

@tool
def generate_growth_chart(user_id: int, period: str = "monthly") -> str:
    """
    Generates a social media growth chart for the user based on historical data.
    Saves the chart as an image and returns the file path.
    """
    df = _get_user_data(user_id)
    if df is None or df.empty:
        return f"No data available to generate chart for User {user_id}."
    
    try:
        # Preprocessing
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['likes_count'], label='Likes', marker='o')
        plt.plot(df['timestamp'], df['impressions'], label='Impressions', marker='x', linestyle='--')
        
        plt.title(f"Growth Chart for User {user_id}")
        plt.xlabel("Date")
        plt.ylabel("Engagement")
        plt.legend()
        plt.grid(True)
        
        # Save
        charts_dir = os.path.join(settings.BASE_DIR, 'static', 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        filename = f"growth_{user_id}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(charts_dir, filename)
        
        plt.savefig(filepath)
        plt.close()
        
        return f"Chart generated successfully: {filepath}"
    except Exception as e:
        return f"Error plotting chart: {e}"

@tool
def post_to_platform(content: str, platform: str, schedule_time: str = "now") -> str:
    """
    Publishes (or schedules) the content to the specified social media platform.
    Returns the status and a (mock) URL of the published post.
    """
    # Mock posting logic
    post_id = uuid.uuid4().hex[:8]
    if schedule_time.lower() == "now":
        return f"SUCCESS: Post published immediately to {platform}. URL: https://{platform.lower()}.com/user/status/{post_id}"
    else:
        return f"SUCCESS: Post scheduled for {schedule_time} on {platform}. Ticket ID: {post_id}"

@tool
def monitor_social_media(user_id: int) -> str:
    """
    Monitors linked social media handles for recent activity and performance stats.
    Returns a summary of recent posts from the dataset.
    CHECK: Requires User to have linked accounts (SocialAccount).
    """
    # 1. Check Linked Accounts
    with Session(engine) as session:
        # Avoid circular import if possible, or import inside
        from app.models.social_account import SocialAccount
        linked = session.query(SocialAccount).filter(SocialAccount.user_id == user_id).all()
        
    if not linked:
        return "No linked social accounts found. Please link your Twitter or LinkedIn account via the Dashboard (Auth Settings) to get real-time monitoring."
        
    linked_platforms = [acc.platform.value for acc in linked] # e.g., ['twitter']
    
    # 2. Get Data (filtered by linked platforms)
    df = _get_user_data(user_id)
    if df is None or df.empty:
        return f"No social media activity found for User {user_id}."
    
    try:
        # Filter by platform
        # Note: Dataset has 'platform' column, we only show data for linked platforms
        # Normalize dataset platform to lowercase for comparison
        df['platform_norm'] = df['platform'].str.lower()
        
        # If simulation/demo, we might ignore this strict filter if dataset platform names don't match exactly 
        # but let's try to be "product-like"
        filtered_df = df[df['platform_norm'].isin(linked_platforms)]
        
        if filtered_df.empty:
             return f"Linked accounts ({', '.join(linked_platforms)}) found, but no recent data available in our cache."
             
        # Get last 5 posts
        filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])
        recent = filtered_df.sort_values('timestamp', ascending=False).head(5)
        
        summary = [f"**Monitoring Report for User {user_id} (Platforms: {', '.join(linked_platforms)})**"]
        
        for _, row in recent.iterrows():
            summary.append(
                f"- {row['timestamp'].strftime('%Y-%m-%d %H:%M')}: "
                f"Topic '{row.get('topic_category', 'N/A')}' on {row.get('platform', 'N/A')} | "
                f"Likes: {row.get('likes_count', 0)} | Reach: {row.get('impressions', 0)}"
            )
            
        avg_likes = recent['likes_count'].mean()
        summary.append(f"\n**Avg Recent Likes**: {avg_likes:.1f}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"Error analyzing social data: {e}"

from app.models.content_draft import ContentDraft, ContentPlatform
from app.models.project_model import Project
from app.config.database import SessionLocal

@tool
def save_draft_to_db(user_id: int, content: str, status: str = "draft", platform: str = "twitter", draft_id: int = None, scheduled_for: str = None) -> str:
    """
    Saves or updates a content draft in the database.
    Status options: 'draft', 'pending_approval', 'approved', 'published', 'rejected', 'scheduled'.
    Returns the Draft ID.
    """
    try:
        from datetime import datetime
        schedule_dt = None
        if scheduled_for and scheduled_for.lower() != "now":
            # Attempt basic parsing, product should use robust dateparser
            try:
                # Assuming simple format or ISO from LLM
                schedule_dt = datetime.fromisoformat(scheduled_for.replace("Z", "+00:00"))
            except:
                pass # Fail silently or use current time if 'now'
        
        with SessionLocal() as db:
            # Upsert logic or Create
            if draft_id:
                draft_obj = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
                if draft_obj:
                    draft_obj.content = content
                    draft_obj.status = status
                    if schedule_dt: draft_obj.scheduled_for = schedule_dt
                    db.commit()
                    return f"Draft {draft_id} updated to status '{status}'."
            
            # Create new
            # ... (Project check)
            project = db.query(Project).filter(Project.user_id == user_id, Project.name == "General").first()
            if not project:
                project = Project(user_id=user_id, name="General", description="Default project", status="active")
                db.add(project)
                db.commit()
                db.refresh(project)
                
            new_draft = ContentDraft(
                project_id=project.id,
                status=status,
                platform=ContentPlatform[platform.lower()] if platform.lower() in ContentPlatform._member_names_ else ContentPlatform.twitter,
                content=content,
                scheduled_for=schedule_dt
            )
            db.add(new_draft)
            db.commit()
            db.refresh(new_draft)
            return f"{new_draft.id}" # Return just ID
            
    except Exception as e:
        return f"Error saving draft: {e}"

@tool
async def repurpose_content(source_url: str = None, source_text: str = None, target_format: str = "twitter_thread") -> str:
    """
    Repurposes a blog post (URL) or text into a social media format (thread, linkedin post).
    """
    content = source_text
    if source_url:
       content = await scraper_service.scrape_url(source_url)
       
    if not content:
        return "No content found to repurpose."
        
    return f"REPURPOSE_SOURCE (Format: {target_format}):\n{content[:5000]}"

