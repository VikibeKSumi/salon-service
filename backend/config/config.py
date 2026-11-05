import os, yaml
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env.local")


class SalonServiceConfiguration():

    def __init__(self):
        config_path = Path(__file__).parent/ "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # from secrets
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.TG_SECRET = os.getenv("TELEGRAM_SECRET")
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.POSTGRES_URL = os.getenv("POSTGRES_URL")
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        
        # from config.yaml
        self.TG_URL = config_data["telegram"]["tg_url"]+self.TELEGRAM_TOKEN
        self.TG_TTL = config_data["telegram"]["tg_ttl"]
        self.SESSION_TTL = config_data["auth"]["session_ttl"]
        self.FRONTEND_ORIGINS = config_data["frontend"]["frontend_origin"]
        
config = SalonServiceConfiguration()