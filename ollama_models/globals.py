# This globals file contains global variables that are used in app.py
# to serve the custom tinyLlama model
import os 
from typing import Dict

OLLAMA_ENDPOINT: str = "http://localhost:11434/api/generate"
MODEL_NAME: str = "tinyllama"

# Default generation config optimized for 1B model
DEFAULT_GENERATION_CONFIG: Dict = {
    "temperature": 0.3,
    "top_p": 0.3,
}

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "<your-auth-token>") 