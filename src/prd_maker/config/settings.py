"""Application configuration and settings."""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = None


@dataclass
class AppConfig:
    """Main application configuration."""
    app_name: str = "PRD Maker"
    version: str = "0.1.0"
    debug: bool = False
    
    # Model configurations
    default_model: str = "gpt-4"
    models: Dict[str, ModelConfig] = None
    
    # Storage settings
    use_local_storage: bool = True
    storage_key: str = "prd_maker_data"
    
    def __post_init__(self):
        if self.models is None:
            self.models = self._get_default_models()
    
    def _get_default_models(self) -> Dict[str, ModelConfig]:
        """Get default model configurations."""
        return {
            "gpt-4": ModelConfig(
                name="gpt-4",
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                model_params={"temperature": 0.7}
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                model_params={"temperature": 0.7}
            ),
            "claude-3-sonnet": ModelConfig(
                name="claude-3-sonnet-20240229",
                provider="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model_params={"temperature": 0.7}
            ),
            "claude-3-haiku": ModelConfig(
                name="claude-3-haiku-20240307",
                provider="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model_params={"temperature": 0.7}
            ),
            "llama2": ModelConfig(
                name="llama2",
                provider="ollama",
                base_url="http://localhost:11434",
                model_params={"temperature": 0.7}
            ),
            "codellama": ModelConfig(
                name="codellama",
                provider="ollama",
                base_url="http://localhost:11434",
                model_params={"temperature": 0.7}
            ),
        }


# Global configuration instance
config = AppConfig(
    debug=os.getenv("DEBUG", "false").lower() == "true"
)