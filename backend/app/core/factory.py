from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.config.settings import settings

class MultiModelFactory:
    """
    Factory to get the appropriate LLM based on the use case.
    """
    
    @staticmethod
    def get_llm(model_type: str = "fast", temperature: float = 0.7) -> BaseChatModel:
        """
        Returns an LLM instance based on model_type.
        
        Args:
            model_type: 'creative' (Google Gemini) or 'fast' (Groq/Llama)
            temperature: Creativity of the model
        """
        if model_type == "creative":
            # Uses Google Gemini for high-quality, complex reasoning tasks
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=temperature,
                google_api_key=settings.GOOGLE_API_KEY,
                convert_system_message_to_human=True # Sometimes needed for Gemini
            )
            
        elif model_type == "fast":
            # Uses Groq for speed and short-form content
            return ChatGroq(
                model_name="llama3-70b-8192",
                temperature=temperature,
                # api_key handled by env GROQ_API_KEY
            )
            
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    @staticmethod
    def get_brain(agent_role: str) -> BaseChatModel:
        """
        Helper to map agent roles to model types.
        """
        if agent_role in ["scripter", "critic"]:
            return MultiModelFactory.get_llm(model_type="creative")
        else:
            return MultiModelFactory.get_llm(model_type="fast")
