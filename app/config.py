import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# JWT Configuration
# ==========================

SECRET_KEY = os.getenv("SECRET_KEY", "pennywise_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================
# Gemini API
# ==========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================
# Email Configuration
# ==========================

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")