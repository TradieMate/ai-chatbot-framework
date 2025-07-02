import os
import dotenv
from pydantic import BaseModel

dotenv.load_dotenv()


class BaseConfig(BaseModel):
    DEBUG: bool = False
    Development: bool = False

    # Database Configuration (supports both MongoDB and PostgreSQL)
    MONGODB_HOST: str = "mongodb://127.0.0.1:27017"
    MONGODB_DATABASE: str = "ai-chatbot-framework"
    
    # PostgreSQL/Supabase Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_chatbot_framework")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    
    # Use PostgreSQL if DATABASE_URL is provided
    USE_POSTGRESQL: bool = bool(os.getenv("DATABASE_URL"))

    # Model Configuration
    MODELS_DIR: str = "model_files/"
    DEFAULT_FALLBACK_INTENT_NAME: str = "fallback"
    DEFAULT_WELCOME_INTENT_NAME: str = "init_conversation"
    SPACY_LANG_MODEL: str = "en_core_web_md"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
    
    # LLM Configuration
    USE_LLM_NLU: bool = os.getenv("USE_LLM_NLU", "false").lower() == "true"
    USE_ZERO_SHOT_NLU: bool = os.getenv("USE_ZERO_SHOT_NLU", "false").lower() == "true"


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    Development: bool = True
    TEMPLATES_AUTO_RELOAD: bool = True


class TestingConfig(BaseConfig):
    DEBUG: bool = True
    TESTING: bool = True


class ProductionConfig(BaseConfig):
    SPACY_LANG_MODEL: str = "en_core_web_md"


config = {
    "Development": DevelopmentConfig,
    "Testing": TestingConfig,
    "Production": ProductionConfig,
}


def from_envvar():
    """Get configuration class from environment variable."""
    choice = os.environ.get("APPLICATION_ENV", "Development")
    if choice not in config:
        msg = "APPLICATION_ENV={} is not valid, must be one of {}".format(
            choice, set(config)
        )
        raise ValueError(msg)
    loaded_config = config[choice](**os.environ)
    return loaded_config
