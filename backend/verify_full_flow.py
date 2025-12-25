import os
import asyncio
from app.agents.graph import app
from app.agents.state import AgentState

# Ensure API Keys are present
if not os.getenv("GROQ_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: API Keys not set. This test might fail.")

async def run_test():
    print("--- Starting Sentry Flow Verification ---")
    
    initial_state = {
        "input": "Create a post about the future of AI Agents in 2025.",
        "user_id": 1,
        "model_provider": "gemini",
        "chat_history": [],
        "revision_count": 0,
        "is_good_enough": False,
        "sentry_approval_status": "pending"
    }
    
    print(f"Initial State: {initial_state}")
    
    try:
        print("\n--- Running Graph ---")
        async for output in app.astream(initial_state):
             for node_name, state_update in output.items():
                print(f"\n[Node: {node_name}]")
                if "draft" in state_update:
                    print(f"Draft Snippet: {state_update['draft'][:50]}...")
                if "sentry_approval_status" in state_update:
                     print(f"Sentry Status: {state_update['sentry_approval_status']}")
                     
        print("\n--- Graph Execution Paused/Ended ---")
        
    except Exception as e:
        print(f"Error executing graph: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
