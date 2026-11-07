
import requests, time
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from capability_services.capability_services import CapabilityService
from schemas.capability_services_schema import GetOrCreateCustomerInput, HandoffInput

class TelegramService():

    def __init__(
            self,
            tg_url: str,
            graph: CompiledStateGraph,
            service: CapabilityService,
        ):
        self.tg_url = tg_url
        self.graph = graph
        self.service = service

    def tg_send(self, chat_id: int, reply_text: str) -> None: # send response to telegram operation is done here.
        for attempt in range(3):
            try:
                r = requests.post(
                url=f"{self.tg_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": reply_text,
                    },
                timeout=10
                )
                r.raise_for_status()  # 4xx/5xx don't raise by default; make them raise so except retries
                return
            except requests.RequestException as e:
                print(f"tg_send attempts {attempt+1} failed: {e}")
                time.sleep(1)


    # def get_reply(self, user_id: int, text: str) -> str: # text response to the query is created here
    #     return f"{user_id}: {text}"


    def handle(self, response: dict) -> None:
        msg = response.get("message", {})
        if not msg:
            return
        
        user_id = msg["from"]["id"] 
        first_name = msg["from"]["first_name"]
        chat_id = msg["chat"]["id"]
        
        if "text" not in msg: # non text message handling
            self.tg_send(chat_id, reply_text="I can only read text messages") 
            return
        text = msg["text"]

        graph_config = {
            "configurable": {"thread_id": str(user_id)}
        }
        try:
            customer_info = self.service.get_or_create_customer( 
                request=GetOrCreateCustomerInput(telegram_id=user_id, name=first_name)
            ).payload.model_dump(mode="json")  # create a new record of customer if they does not yet exists. and get them if them.

            if not self.service.is_handoff_active(
                request=HandoffInput(telegram_id=user_id)
            ).payload:  # check if user is in conversation with a human.
                reply_text = self.graph.invoke(
                    input={
                        "messages": HumanMessage(content=text),
                        "telegram_id": user_id,
                        "customer_info": customer_info,
                    },
                    config=graph_config
                )["messages"][-1].content
            else:
                reply_text = "You're connected to staff; they'll reply here"
            

        except Exception as e:
            reply_text = "Sorry, something went wrong with agent. Please try again"
            print(e)
        self.tg_send(chat_id, reply_text)
        return

