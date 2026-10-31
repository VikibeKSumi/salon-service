from fastapi import FastAPI
from pydantic import BaseModel, Field
import requests


app = FastAPI(title="Salon Service")

class ChatRequest(BaseModel):
    query: str = Field()


@app.get("/")
def home():

    return {
        "Status": "Running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    requests.post()
    response = "response" #llm.invoke(input=request.query)
    return {
        "query": request.query,
        "response": response
    }

