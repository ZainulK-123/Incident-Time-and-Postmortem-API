
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server with proper SSL configuration
client = MongoClient(
    uri, 
    server_api=ServerApi('1'),
    tlsCAFile=certifi.where(),
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=30000
)

db = client.incident_db

# Collections
incidents_collection = db["incidents"]
timeline_collection = db["timeline_events"]
postmortem_collection = db["postmortems"]
