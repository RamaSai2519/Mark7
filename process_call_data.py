from process_call_recording import process_call_recording
from upload_transcript import upload_transcript
from sentiment import get_tonality_sentiment
from config import callsmeta_collection, calls_collection


def process_call_data(call, user, expert, database, usercallId, expertcallId):
    customer_persona = usercallId.get("Customer Persona", "None")

    (
        transcript,
        summary,
        conversation_score,
        conversation_score_details,
        saarthi_feedback,
        customer_persona,
        user_callback,
        topics,
    ) = process_call_recording(call, user, expert, customer_persona)
    
    if not transcript or not customer_persona:
        return False


    sentiment = get_tonality_sentiment(transcript)

    transcript_url = upload_transcript(transcript, call["callId"])

    update_query = {"_id": usercallId["_id"]}
    update_values = {"$set": {"Customer Persona": customer_persona}}
    database.users.update_one(update_query, update_values)

    update_values = {
        "callId": call["callId"],
        "user": usercallId["_id"],
        "expert": str(expertcallId["_id"]),
        "Conversation Score": conversation_score,
        "Score Breakup": conversation_score_details,
        "Sentiment": sentiment,
        "Saarthi Feedback": saarthi_feedback,
        "User Callback": user_callback,
        "Topics": topics,
        "Summary": summary,
        "transcript_url": transcript_url,
    }
    callsmeta_collection.insert_one(update_values)

    calls_collection.update_one(
        {"callId": call["callId"]},
        {"$set": {"Conversation Score": conversation_score}},
    )
    return True
