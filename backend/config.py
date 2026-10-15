"""Configuration for MuryaAI - N-ATLAS Voice-First Citizen Resolution Agent.
NAIC 2026 Innovation & Enterprise Track Submission.
"""
import os
from pathlib import Path
from pydantic import BaseModel

# Automatically load .env if present in root or current dir
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

class Settings(BaseModel):
    APP_NAME: str = "MuryaAI (N-VoiceCare)"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Voice-First Citizen & Consumer Grievance Resolution Infrastructure powered by N-ATLAS"
    
    # N-ATLAS Configuration
    NATLAS_MODEL_REPO: str = os.getenv("NATLAS_MODEL_REPO", "NCAIR1/N-ATLaS")
    # Can be HuggingFace Inference API or live Kaggle/vLLM ngrok server e.g. https://...ngrok-free.app/v1/chat/completions
    NATLAS_API_URL: str = os.getenv(
        "NATLAS_API_URL", 
        "https://api-inference.huggingface.co/models/NCAIR1/N-ATLaS"
    )
    NATLAS_API_KEY: str = os.getenv("NATLAS_API_KEY", "")
    
    # Execution mode: 'hybrid' uses live API if key is present, falls back gracefully to local deterministic reasoning
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "hybrid")
    
    # Supported Languages
    SUPPORTED_LANGUAGES: list[str] = [
        "hausa",
        "yoruba",
        "igbo",
        "nigerian_english"
    ]
    
    # Telephony Providers
    AFRICASTALKING_USERNAME: str = os.getenv("AT_USERNAME", "sandbox")
    AFRICASTALKING_API_KEY: str = os.getenv("AT_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Host settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
