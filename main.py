from process_call_data import process_call_data
from score_updater import updater
from notify import notify
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
    print("Main loop running")
    for change in stream:
        call = change["fullDocument"]
        user_document = users_collection.find_one({"_id": call["user"]})
        expert_document = experts_collection.find_one({"_id": call["expert"]})
        if not user_document or not expert_document:
            continue
        duration = call["duration"] if "duration" in call else "00:00:00"
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 120:
            try:
                user = user_document["name"]
                expert = expert_document["name"]
                notify(
                    f"Processing call {str(call["callId"])} between {
                        user} and {expert} on main loop"
                )
                user_calls = calls_collection.count_documents(
                    {"user": call["user"]})
                call_processed = process_call_data(
                    call, user, expert, db, user_document, user_calls)
                if not call_processed:
                    continue
                updater(call["expert"], call["callId"])
            except Exception as e:
                error_message = f"An error occurred processing the call ({call.get('callId')}): {
                    str(e)} on main loop"
                notify(error_message)
                continue
