"""
Configuration settings for Nango Jira Integration Backend
"""
import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self):
        # Nango Configuration
        self.nango_host = os.environ.get("NANGO_HOST", "https://app.nango.codemateai.dev")
        self.nango_secret_key = os.environ.get("NANGO_SECRET_KEY", "")
        self.nango_public_key = os.environ.get("NANGO_PUBLIC_KEY", "")
        self.nango_jira_provider_key = os.environ.get("NANGO_JIRA_PROVIDER_KEY", "jira")

        # MongoDB Configuration
        self.mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
        self.mongodb_db_name = os.environ.get("MONGODB_DB_NAME", "nango_jira_demo")

        # Application Settings
        self.api_host = os.environ.get("API_HOST", "0.0.0.0")
        self.api_port = int(os.environ.get("API_PORT", "8000"))
        self.debug = os.environ.get("DEBUG", "True").lower() == "true"

        # CORS
        self.frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def get_settings():
    """Get settings instance"""
    return Settings()
