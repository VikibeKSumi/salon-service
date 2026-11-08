
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SalonState(TypedDict):
    # accumulator
    messages: Annotated[list[BaseMessage], add_messages] #seeded too

    #seeded
    telegram_id: int
    customer_info: dict | None

    #routing fields
    next_node: str

    #payload
    booking_info: dict | None
    email_sent: bool

    #explanation
    agent_response: str | None
    email_response: str | None