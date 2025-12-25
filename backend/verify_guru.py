import os
import asyncio
from app.agents.graph import app
from app.agents.state import AgentState

if not os.getenv("GROQ_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: API Keys not set.")

async def run_test():
    print("--- Starting Guru (Chatbot) Verification ---")
    
    # Test Query 1: Brand Voice (Requires RAG)
    q1 = {
        "input": "What is my brand voice guidelines?",
        "user_id": 1,
        "model_provider": "gemini",
        "chat_history": []
    }
    print(f"\nUser: {q1['input']}")
    
    async for output in app.astream(q1):
         for node_name, state_update in output.items():
            print(f"[Node: {node_name}]")
            if "chat_history" in state_update:
                answer = state_update['chat_history'][-1].content
                print(f"Guru: {answer}\n")
                
    # Test Query 2: Monitoring (Requires Data Tool)
    q2 = {
        "input": "Show me my social media growth.",
        "user_id": 1,
        "model_provider": "gemini",
        "chat_history": []
    }
    print(f"\nUser: {q2['input']}")
    
    async for output in app.astream(q2):
         for node_name, state_update in output.items():
            print(f"[Node: {node_name}]")
            if "chat_history" in state_update:
                answer = state_update['chat_history'][-1].content
                print(f"Guru: {answer}\n")

if __name__ == "__main__":
    asyncio.run(run_test())
