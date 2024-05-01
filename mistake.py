from pymongo import MongoClient
from time import sleep
from bson import ObjectId
import datetime
import pprint

client = MongoClient(
    "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["test"]
collection = db["calls"]

document = {
    "callId": "cd19bfee-38b8-4535-94b6-d484fa9fa45f",
    "status": "successfull",
    "initiatedTime": datetime.datetime(2024, 4, 30, 11, 5, 30, 772000),
    "duration": "0:00:48",
    "transferDuration": "00:00:00",
    "recording_url": "None",
    "failedReason": "call missed",
    "expert": ObjectId("66046d7b42f04a057fa210c4"),
    "user": ObjectId("6630d04399906e1d9d9c0560"),
    "__v": 0,
}

collection.insert_one(document)
print("Document inserted successfully.")

sleep(1)

collection.delete_one({"callId": "cd19bfee-38b8-4535-94b6-d484fa9fa45f"})
print("Document deleted successfully.")

calls = list((collection.find({"callId": "cd19bfee-38b8-4535-94b6-d484fa9fa45f"})))
pprint.pprint(calls)
