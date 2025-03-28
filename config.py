import os
from dotenv import load_dotenv

# Load from .env if running locally
if os.getenv("FLASK_ENV") == "development":
    load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
#WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
CRM_API_URL = os.getenv("CRM_API_URL")
# PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
PIPEDRIVE_API_TOKEN = os.getenv("PIPEDRIVE_API_TOKEN")
#VERIFY_TOKEN  = os.getenv("VERIFY_TOKEN")
#PIPEDRIVE_COMPANY_DOMAIN = os.getenv("PIPEDRIVE_COMPANY_DOMAIN")


PIPEDRIVE_COMPANY_DOMAIN = "metamorphicdesigns.pipedrive.com"
VERIFY_TOKEN = "EAAHQcZA9BtxwBO7J9NB5LMQYW4UAN5S9"
WHATSAPP_API_URL="https://graph.facebook.com/v15.0/654782207707781/messages"
PHONE_NUMBER_ID = "588288327707599"
AZ_ACCESS_TOKEN = os.getenv("AZ_ACCESS_TOKEN")