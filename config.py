
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://zk863054_db_user1:08xFKui3RDNscJyT@cluster0.dcs5shz.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.incident_db

# Collections
incidents_collection = db["incidents"]
timeline_collection = db["timeline_events"]
postmortem_collection = db["postmortems"]
