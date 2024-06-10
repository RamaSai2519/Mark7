from config import model, retry_interval_seconds, DEEPGRAM_API_KEY
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
from download_audio import download_audio
from notify import notify
import logging
import time
import json
import re
import os

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def process_call_recording(document, user, expert, persona):
    audio_filename = f"{document['callId']}.mp3"
    logging.info(f"Starting process for call ID: {document['callId']}")

    download_audio(document, audio_filename)
    logging.info(
        f"Downloaded audio for call ID: {document['callId']} to {audio_filename}"
    )

    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        logging.info("Initialized Deepgram client")

        with open(audio_filename, "rb") as file:
            buffer_data = file.read()
            logging.info(f"Read audio file {audio_filename}")

        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="whisper-medium",
        )

        logging.info(f"Sending audio file {audio_filename} for transcription")
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            payload, options, timeout=600
        )
        response = response.to_json(indent=4)
        response = json.loads(response)
        transcript = (
            response.get("results")
            .get("channels")[0]
            .get("alternatives")[0]
            .get("transcript")
        )
        logging.info(f"Transcription completed for call ID: {document['callId']}")

    except Exception as e:
        error_message = f"An error occurred processing the call ({document['callId']}): {str(e)} while transcribing the audio"
        notify(error_message)
        logging.error(error_message)
        notify(f"Retrying after {retry_interval_seconds / 60} minutes...")
        logging.info(
            f"Retrying after {retry_interval_seconds / 60} minutes due to error"
        )
        return None, None, None, None, None, None, None, None

    os.remove(audio_filename)
    logging.info(f"Removed audio file {audio_filename}")

    chat = model.start_chat(history=[])
    logging.info(f"Started chat session for call ID: {document['callId']}")

    try:
        chat.send_message(
            f"I'll give you a call transcript between the user {user} and the expert(saarthi) {expert}, who connected via a website called 'Sukoon.Love', a platform for seniors to have conversations and seek expert guidance from experts(saarthis). Study the transcript and answer the questions I ask accordingly"
        ).resolve()
        logging.info(
            f"Sent initial message to chat model for call ID: {document['callId']}"
        )

        chat.send_message(transcript + "\n This is the transcript").resolve()
        logging.info(f"Sent transcript to chat model for call ID: {document['callId']}")

        chat.send_message(
            """
            Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harassment, discrimination, 
            or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong.
            """
        ).resolve()
        logging.info(
            f"Requested analysis of inappropriate content for call ID: {document['callId']}"
        )

        summary = chat.last.text.replace("*", " ")

        if "All good" in summary:
            logging.info(
                f"No inappropriate content found for call ID: {document['callId']}"
            )

            chat.send_message("Summarize the transcript").resolve()
            logging.info(
                f"Requested transcript summary for call ID: {document['callId']}"
            )
            summary = chat.last.text.replace("*", " ")

            chat.send_message("Give me feedback for the saarthi").resolve()
            logging.info(
                f"Requested saarthi feedback for call ID: {document['callId']}"
            )
            saarthi_feedback = chat.last.text.replace("*", " ")

            with open("guidelines.txt", "r", encoding="utf-8") as file:
                guidelines = file.read()
            logging.info("Read guidelines from guidelines.txt")

            chat.send_message(
                f"""
                Please analyze the call transcript between a Saarthi (expert) and a user based on the given parameters.
                Opening Greeting(_/5)- Evaluate if the guidelines given below are followed.
                Tonality(_/10) - Evaluate the diction, imagery, details, language and syntax of the conversation.
                Time split between Saarthi and User(_/15) - Evaluate if the User spent higher time talking or not.
                User Sentiment(_/20) - Evaluate the sentiment of the user.
                Flow Of Conversation(_/10) - Evaluate if the guidelines given below are followed.
                Time Spent on Call(_/15) - Higher the time, Higher the score.
                Probability of the User Calling Back(_/20) - The User should explicitly state that they would call back for a higher score. Also mention the instance if the user explicitly states that they would call back.
                Closing Greeting(_/5) - Evaluate if the guidelines given below are followed.

                Guidelines:
                {guidelines}

                Find the section relating to the parameters in these guidelines before you give a score. Higher score if the guidelines are followed.
                """
            ).resolve()
            logging.info(
                f"Requested detailed conversation analysis for call ID: {document['callId']}"
            )
            conversation_score_details = chat.last.text.replace("*", " ")

            chat.send_message("Give me a total score out of 100").resolve()
            logging.info(f"Requested total score for call ID: {document['callId']}")
            conversation_score = chat.last.text
            conversation_score = re.findall(r"\b(?:\d{2}|100)\b", conversation_score)
            try:
                conversation_score = int(conversation_score[0])
                conversation_score = conversation_score / 20
                logging.info(
                    f"Calculated total score: {conversation_score} for call ID: {document['callId']}"
                )
            except Exception as e:
                logging.error(f"Error calculating total score: {str(e)}")
                conversation_score = 0

            if persona != "None":
                chat.send_message(
                    f"""
                    This is the user persona derived from previous call transcripts of the user.
                    User Persona: {persona}

                    Remember this and answer the next question accordingly.
                    """
                ).resolve()
                logging.info(
                    f"Sent user persona to chat model for call ID: {document['callId']}"
                )
            else:
                logging.info(
                    f"No previous user persona provided for call ID: {document['callId']}"
                )

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
            logging.info(
                f"Requested user persona analysis for call ID: {document['callId']}"
            )
            customer_persona = chat.last.text.replace("*", " ")

            chat.send_message(
                """
                Calculate the probability of the user calling back.
                """
            ).resolve()
            logging.info(
                f"Requested probability of callback for call ID: {document['callId']}"
            )
            user_callback = chat.last.text.replace("*", " ")

            chat.send_message("Identify the topics they are talking about").resolve()
            logging.info(
                f"Requested topic identification for call ID: {document['callId']}"
            )
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
            logging.warning(
                f"Inappropriate content found for call ID: {document['callId']}"
            )
            return None, None, None, None, None, None, None, None

    except Exception as e:
        notify(f"An error occurred on process_call_recording:{str(e)}")
        logging.error(
            f"An error occurred during chat processing for call ID: {document['callId']}: {str(e)}"
        )
        return e
