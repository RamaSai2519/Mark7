from score_updater import updater
import pymongo
from functions import *
import time

def main():
    db_uri = "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = pymongo.MongoClient(db_uri)
    db = client.test

    while True:
        successful_calls = list(db.calls.find({"status": "successfull"}))

        for call in successful_calls:
            if call["duration"] >= "00:05:00":
                if "Conversation Score" not in call and call.get("recording_url") not in [
                    "None",
                    "",
                ]:
                    f"Processing call: ({call.get('callId')})"
                    error_message = f"Processing call: ({call.get('callId')})"
                    notify(error_message)
                    try:
                        user_document = db.users.find_one({"_id": call.get("user", "")})
                        expert_document = db.experts.find_one(
                            {"_id": call.get("expert", "")}
                        )
                        user = user_document["name"]
                        expert = expert_document["name"]
                        process_call_data([call], user, expert, db, user_document)
                        updater()
                    except Exception as e:
                        error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)}"
                        notify(error_message)

        time.sleep(3600)


if __name__ == "__main__":
    main()
