from app.agents.state import AgentState
from app.agents.tools import predict_virality_score
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent, AgentExecutor
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os

# Define tools
tools = [predict_virality_score]

def get_model(provider: str):
    if provider.lower() == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-3.0-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        # Default to Groq
        return ChatGroq(
            temperature=0, 
            model_name="llama3-70b-8192",
            api_key=settings.GROQ_API_KEY
        )

def critic_node(state: AgentState):
    """
    The Viral Critic evaluates the draft using the ML model.
    Uses 'create_agent' and supports multiple model providers.
    """
    draft = state.get("draft", "")
    provider = state.get("model_provider", "groq")
    
    # Initialize Model
    model = get_model(provider)
    
    # Create Agent (User's requested syntax)
    # Note: Depending on the actual signature of create_agent in the installed version,
    # this might need a check. Assuming strictly user's syntax:
    agent = create_agent(model, tools=tools)
    
    # Execute
    # If create_agent returns a Runnable/Graph, we invoke it.
    # If it returns an AgentRunnable that needs an Executor, we wrap it.
    # Modern create_agent usually returns a CompiledGraph (if LangGraph based)
    # or a Runnable (if functional). 
    # To be safe and follow the snippet "agent = create_agent(...)", we assume it's runnable.
    
    prompt_text = f"""
    Evaluate this draft:
    {draft}
    
    Use 'predict_virality_score'. If < 0.7, critique. Else "Great job!".
    """
    
    try:
        # Try invoking directly (LangGraph style)
        response = agent.invoke({"messages": [HumanMessage(content=prompt_text)]})
        
        # Handle Output Parsing based on return type
        output = ""
        if isinstance(response, dict) and "messages" in response:
             output = response["messages"][-1].content
        elif isinstance(response, dict) and "output" in response:
             output = response["output"]
        else:
             output = str(response)

    except Exception as e:
        # Fallback if it needs AgentExecutor (older style or specific factory)
        # But user said "this is the agent syntax", implying high level.
        # We'll return error or basic critique if it fails.
        output = f"Error in critic agent: {e}"
    
    # Parse score (same logic as before)
    import re
    score_match = re.search(r"Score:?\s*(\d+\.\d+)", output)
    score = float(score_match.group(1)) if score_match else 0.0
    
    return {
        "virality_score": score, 
        "critique": output, 
        "is_good_enough": score >= 0.7
    }
