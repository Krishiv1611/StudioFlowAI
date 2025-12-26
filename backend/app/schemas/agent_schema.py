from pydantic import BaseModel

class AgentRequest(BaseModel):
    input: str
    model_provider: str = "gemini"
