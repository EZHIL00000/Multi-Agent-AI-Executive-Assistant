"""
Configuration module for the Personal Assistant.

Handles environment variables, LLM initialization, and Google API setup.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel


# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Application configuration loaded from environment variables."""
    
    # Google Gemini API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # LangSmith Tracing
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    
    # User Information
    USER_EMAIL: str = os.getenv("USER_EMAIL", "user@example.com")
    USER_NAME: str = os.getenv("USER_NAME", "User")
    
    # Model Configuration
    # Gemini defaults
    GEMINI_MODEL: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
    # Groq defaults
    GROQ_MODEL: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    
    MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing items."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        return missing


def get_llm(temperature: Optional[float] = None) -> BaseChatModel:
    """
    Get the configured LLM instance. Prefers Groq if GROQ_API_KEY is present.
    
    Args:
        temperature: Override the default temperature setting.
        
    Returns:
        Configured Chat model instance (Groq or Gemini).
        
    Raises:
        ValueError: If no API key is configured.
    """
    # Configure LangSmith tracing if enabled
    if Config.LANGSMITH_TRACING:
        os.environ["LANGSMITH_TRACING"] = "true"
        if Config.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_API_KEY"] = Config.LANGSMITH_API_KEY
            
    temp = temperature if temperature is not None else Config.MODEL_TEMPERATURE

    # Prefer Groq if key is present
    if Config.GROQ_API_KEY:
        return ChatGroq(
            model=Config.GROQ_MODEL,
            temperature=temp,
            groq_api_key=Config.GROQ_API_KEY,
        )
        
    if not Config.GOOGLE_API_KEY:
        raise ValueError(
            "Neither GROQ_API_KEY nor GOOGLE_API_KEY is configured. "
            "Please set at least one in your .env file."
        )
    
    return ChatGoogleGenerativeAI(
        model=Config.GEMINI_MODEL,
        temperature=temp,
        google_api_key=Config.GOOGLE_API_KEY,
    )


# Google API Scopes
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_credentials_path() -> Path:
    """Get the path to Google OAuth credentials file."""
    return Path(__file__).parent.parent / "credentials.json"


def get_token_path() -> Path:
    """Get the path to store OAuth tokens."""
    return Path(__file__).parent.parent / "token.json"
