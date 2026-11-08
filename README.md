# Salon-Service

Salon-Service is a salon service provider with an AI assistant to help you with services. It can create automated bookings, display it, list available services and slots. Users can interact from the telegram messaging platform with the agent and seamlessly get the servicing actions perfomed. 

**Join telegram bot:** [bot link](https://t.me/salon_service_bot) or serach `@salon_service_bot` in telegram app

## Features
- **Webhook**: Set webhook on telegram platform to trigger request on events. Here sending messages on app.
- **Systems interaction**: Multiple APIs interaction. Postgress, redis, telegram, llm, fastapi
- **Agentic service**:
- **Obserability**:
- **local and production separation**:
- **Frontend-backend interaction**:
- **Authentication**:

## Tool stack
- Python
- LangChain
- LangGraph
- LangSmith
- Fast API/REST API
- GCP
- Redis
- Postgres
- Docker
- OpenAI

## System architecture

![System architecture diagram](assets/system.svg)

**Legend**
| Shape | Meaning |
| --- | --- |
plain rectangle | independent system |
| curve rectangel | components |
| single line | call flow | 
| parallel line | dependent on external independent system |

## Known limitaitons
- seen grows forever. Fix: keep only the highest update_id (IDs always increase) or IDs from the last 24h, since retries never come later than that.

## Roadmap
- Integrate with frontend over the api.
- Locust load testing
- Unit testing


**started - 30/10/2026**

