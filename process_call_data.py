from process_call_recording import process_call_recording
from upload_transcript import upload_transcript
from sentiment import get_tonality_sentiment

def process_call_data(call_data, user, expert, database, usercallId):
    customer_persona = usercallId.get("Customer Persona", "None")

    for call in call_data:
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

        sentiment = get_tonality_sentiment(transcript)

        transcript_url = upload_transcript(transcript, call["callId"])

        update_query = {"_id": usercallId["_id"]}
        update_values = {"$set": {"Customer Persona": customer_persona}}
        database.users.update_one(update_query, update_values)

        update_query = {"callId": call["callId"]}
        update_values = {
            "$set": {
                "Conversation Score": conversation_score,
                "Score Breakup": conversation_score_details,
                "Sentiment": sentiment,
                "Saarthi Feedback": saarthi_feedback,
                "User Callback": user_callback,
                "Topics": topics,
                "Summary": summary,
                "transcript_url": transcript_url,
            }
        }
        database.calls.update_one(update_query, update_values)
