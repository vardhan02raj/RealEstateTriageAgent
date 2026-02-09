from pymongo import MongoClient
from config import Config
import certifi

client = MongoClient(
    Config.MONGO_URI,
    tlsCAFile=certifi.where()
)

db = client[Config.DB_NAME]

def get_db():
    return db