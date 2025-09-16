import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# Получаем абсолютный путь к директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Строим абсолютный путь к .env файлу
env_file_path = os.path.join(project_root, ".env")

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=env_file_path, extra='ignore')
    
    BOT_TOKEN: str = ''
    OWNER_CHAT_ID: str = ''
    DATABASE_URL: str = "sqlite+aiosqlite:///default.db"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return self.DATABASE_URL.replace('+aiosqlite', '')

settings = Settings()
assert settings.OWNER_CHAT_ID, 'missing OWNER_CHAT_ID'

if __name__=="__main__":
    print(settings)
