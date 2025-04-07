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



# Databricks configuration
DATABRICKS_JUSTCALL_CONFIG = {
    "server_hostname": "adb-1738127852431756.16.azuredatabricks.net",
    "http_path": "/sql/1.0/warehouses/8cddc035c463a758",
    "access_token": os.getenv("AZ_ACCESS_TOKEN"),
    "catalog_name": "call_catalog",
    "schema_name": "justcall_data",
    "table_name": "calllogs"
}

DATABRICKS_WA_CONFIG = {
    "server_hostname": "adb-1738127852431756.16.azuredatabricks.net",
    "http_path": "/sql/1.0/warehouses/8cddc035c463a758",
    "access_token": os.getenv("AZ_ACCESS_TOKEN"),
    "catalog_name": "whatsapp_catalog",
    "schema_name": "whatsapp_messages",
    "table_name": "whatsappmessages"
}