from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "DrumScore AI API"
    api_prefix: str = "/v1"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
