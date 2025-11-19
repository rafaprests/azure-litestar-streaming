import os
from dotenv import load_dotenv

load_dotenv()

USER_SCOPE_KEY = "auth"
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
