
from pydantic import BaseModel



class BotRequest(BaseModel):
    prompt: str
    phone_number: str

    def __str__(self):
        return f"BotRequest(message='{self.message}', user_id='{self.user_id}', user_name='{self.user_name}', user_phone='{self.user_phone}')"

