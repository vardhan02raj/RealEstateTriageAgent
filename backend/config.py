import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # MongoDB Connection String
    MONGO_URI = os.getenv("MONGO_URI")

    # Database Name
    DB_NAME = os.getenv("DB_NAME", "realestate_db")

    # JWT Secret (used later in auth phase)
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-this")