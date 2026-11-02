from fastapi import FastAPI
from contextlib import asynccontextmanager
import requests

from routes.telegram_route import telegram_router
from config.config import config


TG_SECRET = config.TG_SECRET
TG_URL = config.TG_URL
WEBHOOK_URL = config.WEBHOOK_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    current = requests.get(f"{TG_URL}/getWebhookInfo").json()["result"]["url"]
    if current != config.WEBHOOK_URL:
        r = requests.post(
            url=f"{TG_URL}/setWebhook",
            json={
                "url": WEBHOOK_URL,
                "secret_token": TG_SECRET
            }
        )
        print(r.json())
    else:
        print("Webhook already set")
    yield       # app runs here
                # code after yield runs on shutdown


app = FastAPI(title="Salon Service", lifespan=lifespan)
app.include_router(telegram_router)

@app.get("/")
def home():
    return {
        "Status": "Running"
    }

