import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
CRM_API_URL = os.getenv("CRM_API_URL")
