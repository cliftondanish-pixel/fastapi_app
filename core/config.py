from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    OTP_TOKEN_EXPIRE_MINUTES: int
    
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    
    SMTP_SERVER: str
    SMTP_PORT: int
    
    APP_NAME: str
    APP_VERSION: str
    

    class Config:
        env_file = ".env"

settings = Settings()