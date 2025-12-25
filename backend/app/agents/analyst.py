from app.agents.state import AgentState
from app.services.ml_service import MLService
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os
import json

# Initialize Service
ml_service = MLService()

def get_model(provider: str):
    # Analyst needs logic, Gemini Flash is good.
    return ChatGoogleGenerativeAI(
        model="gemini-3.0-flash",
        temperature=0.2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def analyst_node(state: AgentState):
    """
    The Analyst Agent determines the optimal posting schedule and predicts reach.
    It simulates different times using the ML model to find the best slot.
    """
    user_id = state.get("user_id", 1)
    draft = state.get("draft", "")
    trend_data = state.get("trend_data", "")
    
    # 1. Extract/Infer missing features for the model using LLM
    # We need: platform, topic_category, follower_count (from user profile/state)
    # For now, we mock follower_count or get from state
    follower_count = state.get("follower_count", 50000) # Default/Mock
    
    # 2. Run Schedule Optimization (Grid Search via ML Service)
    base_features = {
        "platform": "Twitter", # Default or extract from draft
        "topic_category": "Technology", # Default or extract
        "follower_count": follower_count,
        "hour_of_day": 12, # Placeholder
        "day_of_week": "Monday" # Placeholder
    }
    
    recommendations = ml_service.recommend_schedule(base_features)
    
    best_slot = recommendations[0] if recommendations else {"day": "Monday", "hour": 12, "predicted_reach": 0}
    
    # 3. Generate Analysis Report
    output = f"""
    ### Analyst Report
    
    **Predicted Reach**: ~{int(best_slot['predicted_reach'])} Impressions
    **Optimal Posting Time**: {best_slot['day']} at {best_slot['hour']}:00
    
    **Why?**: Based on your follower count ({follower_count}) and topic, this time slot maximizes engagement probability according to our regression model.
    """
    
    return {
        "analyst_report": output,
        "best_time": f"{best_slot['day']} {best_slot['hour']}:00",
        "predicted_reach": best_slot['predicted_reach']
    }
