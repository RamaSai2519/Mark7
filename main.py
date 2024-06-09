from process_call_data import process_call_data
from score_updater import updater
from notify import notify
from Score_corrector import corrector
from config import calls_collection, users_collection, experts_collection, db

pipeline = [
    {
        "$match": {
            "operationType": {"$in": ["insert", "update"]},
            "fullDocument.status": "successfull",
        }
    }
]

with calls_collection.watch(pipeline) as stream:
    print("started...")
    for change in stream:
        call = change["fullDocument"]
        user_document = users_collection.find_one({"_id": call["user"]})
        expert_document = experts_collection.find_one({"_id": call["expert"]})
        duration = call["duration"] if "duration" in call else "00:00:00"
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 300:
            try:
                user = user_document["name"]
                expert = expert_document["name"]
                notify(
                    f"Processing call {str(call["callId"])} between {user} and {expert}"
                )
                process_call_data([call], user, expert, db, user_document)
                corrector(call["callId"])
                updater()
            except Exception as e:
                error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)} on main loop"
                notify(error_message)
