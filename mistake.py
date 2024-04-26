from pymongo import MongoClient
from time import sleep
from bson import ObjectId

client = MongoClient(
    "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["test"]
collection = db["calls"]

document = {
    "callId": "4415def4-c430-46d4-8b65-9b0f3c29a094",
    "status": "successfull",
    "initiatedTime": {"$date": "1713886203302"},
    "duration": "0:10:29",
    "transferDuration": "00:10:23",
    "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3D4415def4-c430-46d4-8b65-9b0f3c29a094",
    "failedReason": "",
    "expert": ObjectId("66046cf842f04a057fa210b4"),
    "user": ObjectId("661794a2a6eca419e58847ff"),
    "__v": 0,
}
    
collection.insert_one(document)
print("Document inserted successfully.")

sleep(5)

collection.delete_one({"callId": "4415def4-c430-46d4-8b65-9b0f3c29a094"})
print("Document deleted successfully.")
