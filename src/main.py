import os
from dotenv import load_dotenv

from .modules.WhatsAppBot import WhatsAppBot


# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    bot = WhatsAppBot()
    bot.run(port=os.getenv('PORT', 8080))

