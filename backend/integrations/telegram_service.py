
import requests, time

class TelegramService():

    def __init__(
            self,
            tg_url: str
        ):
        self.tg_url = tg_url

    def tg_send(self, chat_id: int, reply_text: str) -> None:
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


    def get_reply(self, user_id: int, text: str) -> str:
        return f"{user_id}: {text}"


    def handle(self, response: dict) -> None:
        msg = response.get("message", {})
        if not msg:
            return
        
        user_id = msg["from"]["id"] 
        chat_id = msg["chat"]["id"]
        
        if "text" not in msg:
            self.tg_send(chat_id, reply_text="I can only read text messages") # non text message handling
            return
        text = msg["text"]
        
        try:
            reply_text = self.get_reply(user_id, text)
        except Exception as e:
            reply_text = "Sorry, something went wrong with agent. Please try again"
            print(e)
        self.tg_send(chat_id, reply_text)
        return

