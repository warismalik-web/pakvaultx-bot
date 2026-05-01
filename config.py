import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

BASE_URL = "https://mxcuakzztajvkgtsocln.supabase.co/functions/v1/reseller-api"

MONGO_URL = os.getenv("MONGO_URL")
