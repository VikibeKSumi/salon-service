import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import yaml


class SalonServiceConfiguration():

    def __init__(self):
        config_path = Path(__file__).parent/ "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # from secrets
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.TG_SECRET = os.getenv("TELEGRAM_SECRET")

        # from config.yaml
        self.TG_URL = config_data["telegram"]["tg_url"]+self.TELEGRAM_TOKEN
        self.WEBHOOK_URL = config_data["telegram"]["webhook_url"]
        self.TG_TTL = config_data["telegram"]["tg_ttl"]
        self.REDIS_URL = config_data["db"]["redis_url"]
        self.POSTGRES_URL = config_data["db"]["postgres_url"]
        self.SESSION_TTL = config_data["auth"]["session_ttl"]
        self.FRONTEND_ORIGINS = config_data["frontend"]["frontend_origins"]
config = SalonServiceConfiguration()