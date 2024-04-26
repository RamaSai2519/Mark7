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

document = {
    "callId": "3975dd83-50dc-4be3-81be-1c8b9be31ee1",
    "status": "successfull",
    "initiatedTime": datetime.datetime(2024, 4, 26, 4, 0, 26, 474000),
    "duration": "0:23:03",
    "transferDuration": "00:22:55",
    "recording_url": "https://sr.knowlarity.com/vr/fetchsound/?callid%3D3975dd83-50dc-4be3-81be-1c8b9be31ee1",
    "failedReason": "",
    "expert": ObjectId("6604665042f04a057fa20ddc"),
    "user": ObjectId("661526bc6159273a018e7b89"),
    "__v": 0,
}

# collection.insert_one(document)
# print("Document inserted successfully.")

# sleep(5)

# collection.delete_one({"callId": "3975dd83-50dc-4be3-81be-1c8b9be31ee1"})
# print("Document deleted successfully.")

calls = list((collection.find({"callId": "3975dd83-50dc-4be3-81be-1c8b9be31ee1"})))
pprint.pprint(calls)
