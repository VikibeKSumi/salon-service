import uvicorn
from app import app



if __name__ == "__main__":

    server_config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(server_config)
    server.run()
