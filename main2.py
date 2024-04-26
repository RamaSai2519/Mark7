# process_call.py
import google.generativeai as genai
from openai import OpenAI
from urllib.parse import urlparse
import requests
import re
from score_updater import updater
from sentiment import get_tonality_sentiment
from upload_transcript import upload_transcript
import pymongo
import socketio
import os
import time

max_retries = 3
retry_interval_seconds = 3600

socket = socketio.Client()
socket.connect("http://15.206.127.248/")

genai.configure(api_key="AIzaSyC7GliarMdf_jCp6SbKpfzjGwW1IdgFKws")

client = OpenAI(api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")


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


def download_audio(data, filename):
    call_uuid = data["callId"]
    url = data["recording_url"]
    if not url.startswith("http"):
        return None
    url = urlparse(url)
    url = url.scheme + "://" + url.netloc + url.path
    print(call_uuid)
    params = {"callid": call_uuid}
    response = requests.get(url, params=params)
    with open(filename, "wb") as f:
        f.write(response.content)


def process_call_recording(document, user, expert, persona):
    audio_filename = f"{document['callId']}.mp3"
    download_audio(document, audio_filename)
    audio_file = open(audio_filename, "rb")
    try:
        translation = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
            prompt=f"This is a call recording between the user {user} and the expert(saarthi) {expert}, who connected via a website called 'Sukoon.Love', a platform for seniors to have conversations and seek expert guidance from experts(saarthis).",
        )
        transcript = (
            translation.text
            + f"\n This is a call recording between the user {user} and the expert(saarthi) {expert}, who connected via a website called 'Sukoon.Love', a platform for seniors to have conversations and seek expert guidance from experts(saarthis)."
        )
    except Exception as e:
        error_message = (
            f"An error occurred processing the call ({document['callId']}): {str(e)}"
        )
        socket.emit("error_notification", error_message)
        print(error_message)
        socket.emit(f"Retrying after {retry_interval_seconds / 60} minutes...")
        time.sleep(retry_interval_seconds)

    audio_file.close()
    os.remove(audio_filename)
    # Model intitalization with context
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    chat.send_message(
        f"I'll give you a call transcript between the user {user} and the expert(saarthi) {expert}, who connected via a website called 'Sukoon.Love', a platform for seniors to have conversations and seek expert guidance from experts(saarthis). Study the transcript and answer the questions I ask accordingly"
    )
    try:
        chat.send_message(transcript + "\n This is the transcript")

        chat.send_message(
            """
                          Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harrasement, discrimination, 
                          or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong.
                          """
        ).resolve()
        summary = chat.last.text.replace("*", " ")

        if "All good" in summary:
            # Summary
            chat.send_message("Summarize the transcript")
            summary = chat.last.text.replace("*", " ")

            # Feedback for the Saarthi
            chat.send_message("Give me feedback for the saarthi")
            saarthi_feedback = chat.last.text.replace("*", " ")

            # Conversation Score
            with open("guidelines.txt", "r", encoding="utf-8") as file:
                guidelines = file.read()

            chat.send_message(
                f"""
                              Please analyze the call transcript between a Saarthi (expert) and a user based on the given parameters.
                              Opening Greeting(_/5)- Evaluate if the guidelines given below are followed.
                              Tonality(_/10) - Evaluate the diction, imagery, details, language and syntax of the conversation.
                              Time split between Saarthi and User(_/15) - Evaluate if the User spent higher time talking or not.
                              User Sentiment(_/20) - Evaluate the sentiment of the user.
                              Flow Of Conversation(_/10) - Evaluate if the guidelines given below are followed.
                              Time Spent on Call(_/15) - Higher the time, Higher the score.
                              Probability of Calling Back(_/20) - The User should explicitly state that they would call back for a higher score. Also mention the instance if the user explicilty states that they would cal back.
                              Closing Greeting(_/5) - Evaluate if the guidelines given below are followed.

                              Guidelines:
                              {guidelines}

                              Find the section relating to the parameters in these guidelines before you give a score. Higher score if the guidelines are followed.
                              """
            )
            conversation_score_details = chat.last.text.replace("*", " ")

            chat.send_message("Give me a total score out of 100")
            conversation_score = chat.last.text
            conversation_score = re.findall(r"\b3[1-9]|[4-9]\d\b", conversation_score)
            try:
                conversation_score = int(conversation_score[0])
                conversation_score = conversation_score / 20
            except Exception as e:
                conversation_score = 0

            if persona != "None":
                chat.send_message(
                    f"""
                                  This is the customer persona derived from previous call transcripts of the user.
                                  Customer Persona: {persona}

                                  Remember this and answer the next question accordingly.
                                  """
                )
            else:
                pass

            # Customer Demographics
            chat.send_message(
                """
                              Context: Generate a cutomer persona with the information provided above. The persona should encompass demographics, psychographics, and personality traits based on the conversation.

                              a. Customer Demographics:
                              1. Age:
                              2. Gender:
                              3. Ethnicity:
                              4. Education:
                              5. Relationship Status:
                              6. Income:
                              7. Living Status:
                              8. Medical History:
                              9. Location/City:
                              10. Comfort with Technology:

                              b. Customer Psychographics:
                              1. Needs:
                              2. Values:
                              3. Pain Points/ Challenges:
                              4. Motivators:

                              c. Customer Personality:
                              Choose one(Sanguine/Choleric/Melancholic/Phlegmatic)
                              """
            )
            customer_persona = chat.last.text.replace("*", " ")

            # User callback probabiltity
            chat.send_message(
                """
                              Calculate the probability of the user calling back.
                              """
            )
            user_callback = chat.last.text.replace("*", " ")

            chat.send_message("Identify the topics they are talking about")
            topics = chat.last.text.replace("*", " ")
            return (
                transcript,
                summary,
                conversation_score,
                conversation_score_details,
                saarthi_feedback,
                customer_persona,
                user_callback,
                topics,
            )
        else:
            return None, None, None, None, None, None, None, None

    except Exception as e:
        print(3)
        print(e)
        socket.emit("An error occurred while processing the call:", str(e))
        return e


def main():
    db_uri = "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = pymongo.MongoClient(db_uri)
    db = client.test

    while True:
        # Get successful calls
        successful_calls = db.calls.find({"status": "successfull"})

        for call in successful_calls:
            if "Conversation Score" not in call and call.get("recording_url") not in [
                "None",
                "",
            ]:
                try:
                    user_document = db.users.find_one({"_id": call.get("user", "")})
                    expert_document = db.experts.find_one(
                        {"_id": call.get("expert", "")}
                    )
                    user = user_document["name"]
                    expert = expert_document["name"]
                    process_call_data([call], user, expert, db, user_document)
                    print("call processed")
                    updater()
                except Exception as e:
                    error_message = f"An error occurred processing the call ({call.get('callId')}): {str(e)}"
                    socket.emit("error_notification", error_message)
                    print(f"call not processed \n {str(e)}")

        print("Processed all calls. Sleeping for 1 hour...")
        time.sleep(3600)


if __name__ == "__main__":
    main()
