from app.agents.state import AgentState
from app.agents.tools import search_vault, monitor_social_media, generate_growth_chart, repurpose_content
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
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
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are the Guru, a Senior Social Media Strategy Consultant for User {user_id}.
        
        Your Mission:
        - Don't just answer questions; provide STRATEGIC ADVICE.
        - Use Data: Always check `monitor_social_media` or `search_vault` if the user asks about performance or history.
        - Be Proactive: If stats are low, suggest improvements based on Brand Voice.
        
        Tools Available:
        - `search_vault`: search past successful posts/guidelines.
        - `monitor_social_media`: correct way to check current stats/engagement.
        - `generate_growth_chart`: visualizes data.
        
        Current Query: "{user_input}"
        
        If you need to use a tool, do so. If you have the answer, reply conversationally as a Consultant.
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Simple Tool Execution Loop (Draft Mode)
    # In a full LangGraph Agent, we'd use the prebuilt `create_tool_calling_agent`.
    # Here checking for direct tool usage for the immediate turn.
    
    # Format history for prompt
    # Using specific "agent_scratchpad" logic if we were using an AgentExecutor
    # But with raw LLM+Tools:
    
    messages = [
        SystemMessage(content=f"You are the Guru, Senior Consultant. User ID: {user_id}. Check data if asked. Be strategic."),
        *chat_history,
        HumanMessage(content=user_input)
    ]
    
    response = llm_with_tools.invoke(messages)
    
    final_answer = response.content
    
    # Handle Tool Calls Manually (Single Turn)
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for call in response.tool_calls:
            t_name = call['name']
            t_args = call['args']
            
            res = "Error: Tool not found"
            if t_name == "search_vault":
                # Inject user_id if missing or ensuring security
                res = search_vault.invoke({"query": t_args.get("query"), "user_id": user_id})
            elif t_name == "monitor_social_media":
                res = monitor_social_media.invoke({"user_id": user_id})
            elif t_name == "generate_growth_chart":
                res = generate_growth_chart.invoke({"user_id": user_id, "period": t_args.get("period", "monthly")})
            elif t_name == "repurpose_content":
                res = repurpose_content.invoke(t_args)
            
            tool_results.append(f"Tool '{t_name}' Output: {res}")
            
        # Re-prompt LLM with tool output
        follow_up_messages = messages + [response] + [HumanMessage(content="\n".join(tool_results))]
        final_response = llm.invoke(follow_up_messages)
        final_answer = final_response.content
        
    # Append to history
    new_history = list(chat_history)
    new_history.append(HumanMessage(content=user_input)) # Current Q
    new_history.append(HumanMessage(content=final_answer)) # Guru A
    
    return {
        "chat_history": new_history
    }
