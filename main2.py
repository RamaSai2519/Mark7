from process_call_data import process_call_data
from score_updater import updater
from notify import notify
from pprint import pprint
from config import *
import time


while True:
    successful_calls = list(db.calls.find({"status": "successfull"}))

    for call in successful_calls:
        duration = call.get("duration", "00:00:00")
        seconds = sum(
            int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
        )
        if seconds > 300:
            if "Conversation Score" not in call and call.get("recording_url") not in [
                "None",
                "",
            ]:
                f"Processing call: ({call.get('callId')})"
                error_message = f"Processing call: ({call.get('callId')})"
                print(error_message)
                notify(error_message)
                try:
                    user_document = db.users.find_one({"_id": call.get("user", "")})
                    expert_document = db.experts.find_one(
                        {"_id": call.get("expert", "")}
                    )
                    user = user_document["name"]
                    expert = expert_document["name"]
                    pprint(call)
                    print(user, expert)
                    process_call_data([call], user, expert, db, user_document)
                    updater()
                except Exception as e:
                    error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)}"
                    notify(error_message)
                    time.sleep(3600)
