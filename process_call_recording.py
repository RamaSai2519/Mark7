from download_audio import download_audio
from config import model, retry_interval_seconds, DEEPGRAM_API_KEY
from notify import notify
import time
import os
import json

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

import re


def process_call_recording(document, user, expert, persona):
    audio_filename = f"{document['callId']}.mp3"
    download_audio(document, audio_filename)
    try:

        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(audio_filename, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="whisper-medium",
        )

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options, timeout = 600)
        # STEP 4: Print the response
        response = response.to_json(indent=4)
        response = json.loads(response)
        transcript = response.get("results").get("channels")[0].get("alternatives")[0].get("transcript")

    except Exception as e:
        error_message = f"An error occurred processing the call ({document['callId']}): {str(e)} while transcripting the audio"
        notify(error_message)
        notify(f"Retrying after {retry_interval_seconds / 60} minutes...")
        time.sleep(retry_interval_seconds)

    os.remove(audio_filename)

    chat = model.start_chat(history=[])
    chat.send_message(
        f"I'll give you a call transcript between the user {user} and the expert(saarthi) {expert}, who connected via a website called 'Sukoon.Love', a platform for seniors to have conversations and seek expert guidance from experts(saarthis). Study the transcript and answer the questions I ask accordingly"
    ).resolve()
    try:
        chat.send_message(transcript + "\n This is the transcript").resolve()

        chat.send_message(
            """
                          Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harrasement, discrimination, 
                          or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong.
                          """
        ).resolve()
        summary = chat.last.text.replace("*", " ")

        if "All good" in summary:
            chat.send_message("Summarize the transcript").resolve()
            summary = chat.last.text.replace("*", " ")

            chat.send_message("Give me feedback for the saarthi").resolve()
            saarthi_feedback = chat.last.text.replace("*", " ")

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
                              Probability of the User Calling Back(_/20) - The User should explicitly state that they would call back for a higher score. Also mention the instance if the user explicilty states that they would cal back.
                              Closing Greeting(_/5) - Evaluate if the guidelines given below are followed.

                              Guidelines:
                              {guidelines}

                              Find the section relating to the parameters in these guidelines before you give a score. Higher score if the guidelines are followed.
                              """
            ).resolve()
            conversation_score_details = chat.last.text.replace("*", " ")

            chat.send_message("Give me a total score out of 100").resolve()
            conversation_score = chat.last.text
            conversation_score = re.findall(r"\b(?:\d{2}|100)\b", conversation_score)
            try:
                conversation_score = int(conversation_score[0])
                conversation_score = conversation_score / 20
            except Exception as e:
                conversation_score = 0

            if persona != "None":
                chat.send_message(
                    f"""
                                  This is the user persona derived from previous call transcripts of the user.
                                  User Persona: {persona}

                                  Remember this and answer the next question accordingly.
                                  """
                ).resolve()
            else:
                pass

            chat.send_message(
                """
                              Context: Generate a user persona with the information provided above. The persona should encompass demographics, psychographics, and personality traits based on the conversation.

                              a. User Demographics:
                              1. Age:
                              2. Gender:
                              3. Ethnicity:
                              4. Education:
                              5. Marital Status Choose one(Single/Widow/Widower/Divorced/Unmarried):
                              6. Income:
                              7. Living Status Choose one(Alone/With Spouse/With Family):
                              8. Medical History:
                              9. Location/City:
                              10. Comfort with Technology:
                              11. Standard of Living:
                              12. Financial Status:
                              13. Family Members:
                              14. Work Status Choose One(Retired/Active Working/Part-Time/Projects)
                              15. Last Company Worked For:
                              16. Language Preference:
                              17. Physical State Of Being: 

                              b. User Psychographics:
                              1. Needs:
                              2. Values:
                              3. Pain Points/ Challenges:
                              4. Motivators:

                              c. User Personality:
                              Choose one(Sanguine/Choleric/Melancholic/Phlegmatic)
                              """
            ).resolve()
            customer_persona = chat.last.text.replace("*", " ")

            chat.send_message(
                """
                              Calculate the probability of the user calling back.
                              """
            ).resolve()
            user_callback = chat.last.text.replace("*", " ")

            chat.send_message("Identify the topics they are talking about").resolve()
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
        notify("An error occurred on process_call_recording:", str(e))
        return e
