from app.agents.state import AgentState
from app.agents.tools import generate_growth_chart, monitor_social_media, store_in_vault
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os

# Define tools
tools = [generate_growth_chart, monitor_social_media]

def get_model(provider: str):
    if provider.lower() == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-3.0-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        # Default to Groq
        if not settings.GROQ_API_KEY:
             return ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key="missing_key")

        return ChatGroq(
            temperature=0, 
            model_name="llama3-70b-8192",
            api_key=settings.GROQ_API_KEY
        )

def engineer_node(state: AgentState):
    """
    The Engineer Agent (Redefined): Social Media Monitor & Strategist.
    It monitors handles, provides growth charts, and suggests improvements.
    """
    user_id = state.get("user_id", 1)
    provider = state.get("model_provider", "groq")
    
    # Initialize Model
    model = get_model(provider)
    
    # Create Agent
    agent = create_agent(model, tools=tools)
    
    # Logic: The engineer runs to check on the user's status and provide a report.
    # It doesn't necessarily depend on a single draft, but on the user's overall state.
    
    prompt = f"""
    You are a Social Media Graph Engineer.
    Your goal is to monitor the user's social media performance and provide strategic technical insights.
    
    User ID: {user_id}
    
    Tasks:
    1. Monitor the user's social media handles for recent activity using `monitor_social_media`.
    2. Generate a growth chart to visualize progress using `generate_growth_chart`.
    3. Based on this data, suggest 1-2 technical or strategic improvements for growth (e.g., "Post more video content", "Fix bio link").
    
    Provide a concise report.
    """

    try:
        response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
        
        # Handle Output Parsing
        if isinstance(response, dict) and "messages" in response:
             engineer_report = response["messages"][-1].content
        elif isinstance(response, dict) and "output" in response:
             engineer_report = response["output"]
        else:
             engineer_report = str(response)
        
        # Store Report for RAG
        store_in_vault.invoke({
            "content": f"ENGINEER REPORT:\n{engineer_report}",
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"Engineer error: {e}")
        engineer_report = "Error generating Engineer report."
        
    return {"engineer_report": engineer_report}
