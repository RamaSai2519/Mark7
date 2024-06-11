from process_call_data import process_call_data
from Score_corrector import corrector
from score_updater import updater
from notify import notify
from config import db
import logging

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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
                    call_processed = process_call_data(call, user, expert, db, user_document, expert_document)
                    if not call_processed:
                        continue

                    corrector(call["callId"])
                    updater()
                except Exception as e:
                    error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)} on backup loop"
                    notify(error_message)
                    continue
