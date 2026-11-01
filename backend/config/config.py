import os
from pathlib import Path
import yaml


class SalonServiceConfiguration():

    def __init__(self):
        config_path = Path(__file__).parent/ "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.TG_SECRET = os.getenv("TELEGRAM_SECRET")

        self.TG_URL = config_data["telegram"]["tg_url"]+self.TELEGRAM_TOKEN
        self.WEBHOOK_URL = config_data["telegram"]["tg_webhook_url"]

config = SalonServiceConfiguration()