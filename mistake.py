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
    "callId": "410c6294-f409-40c7-bd2c-61c125ffd9a6",
    "status": "successfull",
    "initiatedTime": datetime.datetime(2024, 4, 26, 4, 24, 13, 926000),
    "duration": "0:16:45",
    "transferDuration": "00:16:37",
    "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3D410c6294-f409-40c7-bd2c-61c125ffd9a6",
    "failedReason": "",
    "expert": ObjectId("6604665042f04a057fa20ddc"),
    "user": ObjectId("661526bc6159273a018e7b89"),
    "__v": 0,
}

collection.insert_one(document)
print("Document inserted successfully.")

sleep(5)

collection.delete_one({"callId": "410c6294-f409-40c7-bd2c-61c125ffd9a6"})
print("Document deleted successfully.")

# calls = list((collection.find({"callId": "410c6294-f409-40c7-bd2c-61c125ffd9a6"})))
# pprint.pprint(calls)
