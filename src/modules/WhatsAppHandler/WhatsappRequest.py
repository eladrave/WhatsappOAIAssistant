
from pydantic import BaseModel



class WhatsappRequest(BaseModel):
    Body: str
    From: str
    To: str
    
