from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://adminUser:pIrc3SuPIuxaklxt@incident.pmvvhuh.mongodb.net/")
DB_NAME = "Incident_db"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def get_database():
    return db
