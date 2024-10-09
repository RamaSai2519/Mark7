from process_call_data import process_call_data
from config import db, calls_collection
from score_updater import updater
from notify import notify
import logging
import time

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

print("Backup loop started")
while True:
    successful_calls = list(calls_collection.find({"status": "successful"}))
    if successful_calls:
        for call in successful_calls:
            conScore = call.get("conversationScore", None)
            if conScore is None and call.get("recording_url") not in ["None", ""]:
                duration = call.get("duration", "00:00:00")
                seconds = sum(
                    int(x) * 60**i for i, x in enumerate(reversed(duration.split(":")))
                )
                if seconds > 120:
                    print(f"Processing call {str(call["callId"])}")
                    try:
                        user_document = db.users.find_one(
                            {"_id": call.get("user", "")})
                        expert_document = db.experts.find_one(
                            {"_id": call.get("expert", "")}
                        )
                        if not user_document or not expert_document:
                            continue
                        user = user_document["name"]
                        expert = expert_document["name"]
                        user_calls = calls_collection.count_documents(
                            {"user": call["user"]})
                        notify(
                            f"Processing call {str(call.get('callId'))} between {
                                user} and {expert} on backup loop"
                        )
                        call_processed = process_call_data(
                            call, user, expert, user_document, expert_document, user_calls)
                        if not call_processed:
                            print("Call not processed")
                        else:
                            print("Call processed")
                        updater(str(call["expert"]),
                                expert_document["phoneNumber"])
                    except Exception as e:
                        error_message = f"An error occurred processing the call ({call.get('callId')}): {
                            str(e)} on backup loop"
                        notify(error_message)
                        continue
                        
    time.sleep(1800)
