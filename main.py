from score_updater import updater
from functions import *
import pymongo


def main():
    db_uri = "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = pymongo.MongoClient(db_uri)
    db = client.test
    calls_collection = db.calls
    user_document = None
    expert_document = None

    pipeline = [
        {"$match": {"operationType": "update", "fullDocument.status": "successfull"}}
    ]

    with calls_collection.watch(pipeline) as stream:
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
                    process_call_data([call], user, expert, db, user_document)
                    updater()
                except Exception as e:
                    error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)}"
                    notify(error_message)


if __name__ == "__main__":
    main()
