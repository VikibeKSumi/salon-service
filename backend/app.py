import os, requests
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis
from psycopg_pool import ConnectionPool
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI

from integrations.telegram_service import TelegramService
from capability_services.capability_services import CapabilityService
from capability_services.repository.postgres_repository import PostgresRepository
from routes.telegram_route import telegram_router
from routes.auth_route import auth_router
from routes.owner_route import owner_router
from config.config import config
from agent.workflow import SalonAgent


@asynccontextmanager
async def lifespan(app: FastAPI):

    # secrets
    app.state.tg_secret = config.TG_SECRET
    app.state.tg_token = config.TELEGRAM_TOKEN
    # configs
    app.state.tg_url = config.TG_URL
    app.state.webhook_url = config.WEBHOOK_URL
    app.state.tg_ttl = config.TG_TTL
    app.state.redis_url = config.REDIS_URL
    app.state.postgres_url = config.POSTGRES_URL
    app.state.session_ttl = config.SESSION_TTL
    app.state.llm_model_name = config.LLM_MODEL_NAME
    # client connections
    app.state.redis = redis.from_url(app.state.redis_url, decode_responses=True)
    app.state.pool = ConnectionPool(app.state.postgres_url, min_size=1, max_size=5, open=True)
    app.state.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=app.state.llm_model_name)
    # inits
    app.state.postgres_repo = PostgresRepository(pool=app.state.pool)
    app.state.capability_service = CapabilityService(repo=app.state.postgres_repo)
    app.state.agent = SalonAgent(capability_service=app.state.capability_service, llm=app.state.llm)
    #derived
    app.state.graph = app.state.agent.get_graph()
    app.state.tg_service = TelegramService(tg_url=app.state.tg_url, graph=app.state.graph, capability_service=app.state.capability_service)
    app.state.postgres_repo = PostgresRepository(pool=app.state.pool)

    # check if telegram webhook link has been changed. Replace if so.
    current = requests.get(f"{app.state.tg_url}/getWebhookInfo").json()["result"]["url"]
    if current != app.state.webhook_url:
        r = requests.post(
            url=f"{app.state.tg_url}/setWebhook",
            json={
                "url": app.state.webhook_url,
                "secret_token": app.state.tg_secret
            }
        )
        print(r.json())
    else:
        print("Webhook already set")
    
    yield                                       # app runs here
    app.state.redis.close()                     # code after yield runs on shutdown
    app.state.pool.close()

app = FastAPI(title="Salon Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,   # e.g. ["http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(telegram_router)
app.include_router(auth_router)
app.include_router(owner_router)
@app.get("/")
def home():
    return {
        "Status": "Home Running"
    }

