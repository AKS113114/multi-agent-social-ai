import os
from typing import Dict, Any

class Settings:
    PROJECT_NAME: str = "Prodigal AI Social Media Agency"
    VERSION: str = "1.0.0"
    
    # Ollama Local Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:cloud").replace("ollama run", "").replace("ollama pull", "").strip()
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))
    MAX_LLM_RETRIES: int = 3
    
    # Database Configuration
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    
    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'social_agency.db')}")
    
    # Channels
    CHANNELS: Dict[str, Any] = {
        "Pulse": {
            "name": "Pulse",
            "description": "Short-form video/trend oriented channel. High energy, visual, concise.",
            "max_words": 60,
            "peak_hours": [17, 18, 19, 20, 21],
            "target_style": "Energetic, punchy, trend-aware, visual-first."
        },
        "Forum": {
            "name": "Forum",
            "description": "Community discussion and text-focused platform. Rewards open questions and conversation.",
            "max_words": 150,
            "peak_hours": [12, 13, 14, 18, 19, 20],
            "target_style": "Conversational, inquiry-driven, open-ended, authentic."
        },
        "ProNet": {
            "name": "ProNet",
            "description": "Professional network for career & business insights. Value-focused, polished.",
            "max_words": 200,
            "peak_hours": [8, 9, 10, 11],
            "target_style": "Professional, value-driven, structured, concise, insightful."
        }
    }

settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)
