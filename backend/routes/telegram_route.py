import os
from fastapi import APIRouter, Request, Header, BackgroundTasks 

from integrations.telegram_service import TelegramService
from config.config import config


tg_secret = config.TG_SECRET
tg_url = config.TG_URL

telegram_router = APIRouter()
tg_service = TelegramService(
    tg_url=tg_url
)

seen = set()

@telegram_router.post("/telegram")
async def telegram(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None)
    ):

    if x_telegram_bot_api_secret_token != tg_secret:
        return {}

    response = await request.json()
    if response["update_id"] in seen:
        return {}       
    seen.add(response["update_id"])

    background.add_task(tg_service.handle, response)
    return {}


