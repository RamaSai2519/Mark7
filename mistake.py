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
users = db["users"]

{
    "_id": {"$oid": "662b51f5a88f80756faa7a0b"},
    "callId": "a441a92e-9fbb-4458-b4bf-77e72e31c794",
    "status": "successfull",
    "initiatedTime": {"$date": {"$numberLong": "1714115061370"}},
    "duration": "0:04:10",
    "transferDuration": "00:03:47",
    "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3Da441a92e-9fbb-4458-b4bf-77e72e31c794",
    "failedReason": "",
    "expert": {"$oid": "66046a3d42f04a057fa21034"},
    "user": {"$oid": "66178da6a6eca419e5884569"},
    "__v": {"$numberInt": "0"},
}

document = {
    "callId": "a441a92e-9fbb-4458-b4bf-77e72e31c794",
    "status": "successfull",
    "initiatedTime": datetime.datetime(2024, 4, 26, 7, 4, 21, 370000),
    "duration": "0:04:10",
    "transferDuration": "00:03:47",
    "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3Da441a92e-9fbb-4458-b4bf-77e72e31c794",
    "failedReason": "",
    "expert": ObjectId("66046a3d42f04a057fa21034"),
    "user": ObjectId("66178da6a6eca419e5884569"),
    "__v": 0,
}

# collection.insert_one(document)
print("Document inserted successfully.")

sleep(5)

# collection.delete_one({"callId": "a441a92e-9fbb-4458-b4bf-77e72e31c794"})
print("Document deleted successfully.")

calls = list((collection.find({"callId": "a441a92e-9fbb-4458-b4bf-77e72e31c794"})))
pprint.pprint(calls)