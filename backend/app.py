from fastapi import FastAPI
from pydantic import BaseModel, Field

from routes.telegram_route import telegram_router

app = FastAPI(title="Salon Service")
app.include_router(telegram_router)

class ChatRequest(BaseModel):
    query: str = Field()


@app.get("/")
def home():

    return {
        "Status": "Running"
    }

