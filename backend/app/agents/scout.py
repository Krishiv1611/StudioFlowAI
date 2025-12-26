from app.agents.state import AgentState
from app.agents.tools import search_web, search_vault
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os

# Define tools for the agent
tools = [search_web, search_vault]

def get_model(provider: str):
    if provider.lower() == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-3.0-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        # Default to Groq
        if not settings.GROQ_API_KEY:
            # Prevent crash, allow agent to fail gracefully later or now
            # We can't return None easily if expected to be a ChatModel.
            # But we can let it fail at runtime or return a dummy that errors when invoked.
            # For now, pass a dummy key so it instantiates, but errors on call.
            return ChatGroq(temperature=0.7, model_name="llama3-70b-8192", api_key="missing_key")
            
        return ChatGroq(
            temperature=0.7, 
            model_name="llama3-70b-8192",
            api_key=settings.GROQ_API_KEY
        )

def scout_node(state: AgentState):
    """
    The Trend Scout looks for trending topics based on the input AND brand voice.
    Refactored to use 'create_react_agent' and supports multiple model providers.
    """
    user_id = state.get("user_id", 1)
    topic = state.get("input", "latest tech trends")
    provider = state.get("model_provider", "groq")
    
    # Initialize Model
    model = get_model(provider)
    
    # Create Agent (User's syntax)
    agent = create_agent(model, tools=tools)
    
    prompt = f"""
    You are a Strategic Trend Scout.
    
    Your goal is to find trending topics that align with the user's Brand Voice.
    
    Step 1: Use `search_vault` to find "Brand Voice" or "Brand Guidelines" for user_id {user_id}.
    Step 2: Use `search_web` to find latest trends related to '{topic}'.
    Step 3: Filter and analyze the trends to find those that best fit the Brand Voice.
    
    Return a concise summary of the top trend and why it fits the brand.
    """
    
    try:
        # Invoke Agent
        response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
        
        # Handle Output Parsing
        output = ""
        final_messages = []
        if isinstance(response, dict) and "messages" in response:
             final_messages = response["messages"]
             output = final_messages[-1].content
        elif isinstance(response, dict) and "output" in response:
             output = response["output"]
        else:
             output = str(response)
             
        # Extract research context if possible (tool outputs)
        research_context = [str(m) for m in final_messages if hasattr(m, 'tool_calls')]
        
    except Exception as e:
        output = f"Error in scout agent: {e}"
        research_context = []
    
    return {
        "trend_data": output, 
        "research_context": research_context
    }
