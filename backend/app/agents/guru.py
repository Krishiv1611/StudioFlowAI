from app.agents.state import AgentState
from app.agents.tools import search_vault, monitor_social_media, generate_growth_chart, repurpose_content
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os

# Define Guru Tools
tools = [search_vault, monitor_social_media, generate_growth_chart, repurpose_content]

def get_model(provider: str):
    return ChatGoogleGenerativeAI(
        model="gemini-3.0-flash",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def guru_node(state: AgentState):
    """
    The Guru Agent: Interactive RAG Chatbot & Strategist.
    Acts as a Senior Brand Consultant.
    """
    user_id = state.get("user_id", 1)
    chat_history = state.get("chat_history", [])
    user_input = state.get("input", "")
    
    llm = get_model("gemini")
    
    # Create Agent
    agent = create_agent(llm, tools=tools)
    
    prompt_text = f"""
    You are the Guru, a Senior Social Media Strategy Consultant for User {user_id}.
    
    Your Mission:
    - Don't just answer questions; provide STRATEGIC ADVICE.
    - Use Data: Always check `monitor_social_media` or `search_vault` if the user asks about performance or history.
    - Be Proactive: If stats are low, suggest improvements based on Brand Voice.
    
    Current Query: "{user_input}"
    
    If you need to use a tool, do so. If you have the answer, reply conversationally as a Consultant.
    """
    
    # Execute Agent
    try:
        # Pass conversation history + new prompt
        # We need to format history as messages
        messages = list(chat_history)
        messages.append(HumanMessage(content=prompt_text))
        
        response = agent.invoke({"messages": messages})
        
        # Parse Output
        full_response = ""
        if isinstance(response, dict) and "messages" in response:
             full_response = response["messages"][-1].content
        elif isinstance(response, dict) and "output" in response:
             full_response = response["output"]
        else:
             full_response = str(response)
             
        # Update History
        new_history = list(chat_history)
        new_history.append(HumanMessage(content=user_input)) 
        new_history.append(HumanMessage(content=full_response))
        
        return {
            "chat_history": new_history
        }
        
    except Exception as e:
        return {
             "chat_history": chat_history,
             "error": f"Guru failed: {e}"
        }
