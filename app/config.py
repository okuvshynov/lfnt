from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    original_server_url: str = "http://localhost:8080"  # Default URL to the original server
    original_server_timeout: float = 60.0  # Timeout for requests to original server in seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
