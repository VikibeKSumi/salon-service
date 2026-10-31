import requests


class TelegramService():

    def __init__(
            self,
            telegram_api_url: str,
            my_webhook_url: str
        ):

        self.telegram_api_url = telegram_api_url
        self.my_webhook_url = my_webhook_url


    def set_webhook(self):
        requests.post(
            url=self.telegram_api_url,
            json={
                "url": self.my_webhook_url
            }
        )
    