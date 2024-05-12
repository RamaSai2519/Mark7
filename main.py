from process_call_data import process_call_data
from score_updater import updater
from notify import notify
from pprint import pprint
from config import *

pipeline = [
    {
        "$match": {
            "operationType": {"$in": ["insert", "update"]},
            "fullDocument.status": "successfull",
        }
    }
]

with calls_collection.watch(pipeline) as stream:
    print("Listening for changes...")
    for change in stream:
        call = change["fullDocument"]
        if user_document is None:
            user_document = db.users.find_one({"_id": call["user"]})
        if expert_document is None:
            expert_document = db.experts.find_one({"_id": call["expert"]})
        duration = call.get("duration", "00:00:00")
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 300:
            try:
                user = user_document["name"]
                expert = expert_document["name"]
                pprint(call)
                print(user, expert)
                process_call_data([call], user, expert, db, user_document)
                updater()
            except Exception as e:
                print(e)
                error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)}"
                notify(error_message)
