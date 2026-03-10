from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # AI Service Configuration
    ai_api_key: str
    ai_base_url: Optional[str] = None  # For alternative AI providers like Groq
    ai_model: str = "gpt-4"  # Changed to GPT-4 for better mathematical reasoning
    
    # Mathematical precision settings
    math_validation_enabled: bool = True
    max_calculation_precision_error: float = 1e-10
    
    # Application Configuration
    app_name: str = "AI Math Tutor"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
