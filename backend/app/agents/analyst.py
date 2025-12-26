from app.agents.state import AgentState
from app.agents.tools import recommend_schedule
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os
import json

# Define Tools
tools = [recommend_schedule]

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
    Now powered by an Agent Brain using 'recommend_schedule' tool.
    """
    user_id = state.get("user_id", 1)
    draft = state.get("draft", "")
    trend_data = state.get("trend_data", "")
    follower_count = state.get("follower_count", 50000) # Default/Mock
    
    # Initialize Logic
    llm = get_model("gemini")
    agent = create_agent(llm, tools=tools)
    
    prompt = f"""
    You are the Senior Data Analyst.
    
    Your goal is to determine the optimal posting schedule for the user's content.
    
    Constraint: You MUST use the `recommend_schedule` tool to get real data predictions.
    
    Context:
    - Follower Count: {follower_count}
    - Platform: Twitter (Default)
    - Trend: {trend_data}
    
    1. Call `recommend_schedule` (args: platform='Twitter', follower_count={follower_count}, topic_category='Technology').
    2. Analyze the output.
    3. Return a Final Report summarizing the best time and predicted reach.
    """
    
    try:
        response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
        
        # Parse output
        output_text = ""
        if isinstance(response, dict) and "messages" in response:
             output_text = response["messages"][-1].content
        elif isinstance(response, dict) and "output" in response:
             output_text = response["output"]
        else:
             output_text = str(response)
             
        # We can extract structured data regex if needed, or just trust the report
        # For state compatibility, we might want 'best_time' string.
        # Simple heuristic or Regex
        import re
        # Try to find "Monday at 12:00" pattern
        match = re.search(r"(\w+ at \d{1,2}:\d{2})", output_text)
        best_time = match.group(1) if match else "12:00"
        
        return {
            "analyst_report": output_text,
            "best_time": best_time,
            # "predicted_reach": ... (hard to extract from text without structured output, but report has it)
        }
        
    except Exception as e:
        return {
            "analyst_report": f"Analysis failed: {e}",
            "best_time": "12:00" 
        }
