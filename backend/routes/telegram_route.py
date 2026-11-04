from fastapi import APIRouter, Request, Header, BackgroundTasks 

telegram_router = APIRouter()

@telegram_router.post("/telegram")
async def telegram(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None)
    ):

    if x_telegram_bot_api_secret_token != request.app.state.tg_secret:
        return {}
    
    response = await request.json()
    if not request.app.state.redis.set(
        name=f"dedup:{response['update_id']}",
        value=1,
        nx=True,
        ex=request.app.state.tg_ttl
    ):
        return {}

    background.add_task(request.app.state.tg_service.handle, response)
    return {}


