from process_call_data import process_call_data
from score_updater import updater
from notify import notify
from config import db
from Score_corrector import corrector
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
                try:
                    user_document = db.users.find_one({"_id": call.get("user", "")})
                    expert_document = db.experts.find_one(
                        {"_id": call.get("expert", "")}
                    )
                    if not user_document or not expert_document:
                        continue
                    user = user_document["name"]
                    expert = expert_document["name"]
                    notify(
                        f"Processing call {str(call.get('callId'))} between {user} and {expert}"
                    )
                    process_call_data([call], user, expert, db, user_document, expert_document)
                    corrector(call["callId"])
                    updater()
                except Exception as e:
                    error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)} on backup loop"
                    notify(error_message)
                    time.sleep(3600)
