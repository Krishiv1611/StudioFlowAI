from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

try:
    from app.config.settings import settings
    if settings.GROQ_API_KEY:
        llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", api_key=settings.GROQ_API_KEY)
    else:
        llm = None
except Exception:
    llm = None

def scripter_node(state: AgentState):
    """
    The Content Scripter generates a post draft based on the trend data.
    """
    trend_data = state.get("trend_data", "")
    critique = state.get("critique", "")
    revision_count = state.get("revision_count", 0)
    current_draft = state.get("draft", "")
    
    if critique and revision_count > 0:
        prompt = f"""
        You are an expert Content Creator. Refine the following draft based on the critique.
        
        Original Draft:
        {current_draft}
        
        Critique:
        {critique}
        
        Return the improved draft only.
        """
    else:
        prompt = f"""
        You are an expert Content Creator. Create a viral social media post about this trend:
        
        Trend Info:
        {trend_data}
        
        Keep it engaging, concise, and use hashtags.
        """
    
    if not llm:
        return {"draft": "Error: Groq API Key not configured.", "revision_count": revision_count}
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"draft": response.content, "revision_count": revision_count + 1}
