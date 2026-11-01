import os, requests, uvicorn
from dotenv import load_dotenv
load_dotenv()
from config.config import config
from app import app



if __name__ == "__main__":

    # secrets
    TG_SECRET = os.getenv("TELEGRAM_SECRET")

    # settings
    TG_URL = config.TG_URL
    WEBHOOK_URL = config.WEBHOOK_URL

    current = requests.post(url=f"{TG_URL}/getWebhookInfo").json()["result"]["url"]

    if current != WEBHOOK_URL:
        r = requests.post(
            url=f"{TG_URL}/setWebhook",
            json={
                "url": WEBHOOK_URL,
                "secret_token": TG_SECRET
        })
        print(r.json())
    else:
        print("Webhook already set")

    server_config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(server_config)
    server.run()
    



