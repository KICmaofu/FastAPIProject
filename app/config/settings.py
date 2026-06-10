from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "智能巡检系统"
    APP_VERSION: str = "1.0.0"
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "12305"
    DB_NAME: str = "inspection_system"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 密码配置
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    
    # CORS配置
    # 注意: 当 allow_credentials=True 时，不能使用 "*" 作为 origin
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Ollama配置
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:latest"
    OLLAMA_TIMEOUT: int = 120
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()