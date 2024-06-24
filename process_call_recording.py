from config import model, DEEPGRAM_API_KEY
from download_audio import download_audio
from notify import notify
import logging
import re
import os
import subprocess


def process_call_recording(document, user, expert, persona, user_calls):
    audio_filename = f"{document['callId']}.mp3"
    logging.info(f"Starting process for call ID: {document['callId']}")

    download_audio(document, audio_filename)
    logging.info(
        f"Downloaded audio for call ID: {
            document['callId']} to {audio_filename}"
    )

    try:
        logging.info("Initialized Deepgram client")

        curl_command = [
            'curl',
            '--request', 'POST',
            '--url', 'https://api.deepgram.com/v1/listen?model=whisper-large&diarize=true&punctuate=true&utterances=true',
            '--header', f'Authorization: Token {DEEPGRAM_API_KEY}',
            '--header', 'content-type: audio/mp3',
            '--data-binary', f'@{audio_filename}'
        ]

        # Run the curl command using subprocess
        result = subprocess.run(
            curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None, None, None, None, None, None, None, None
        else:
            # Use jq to process the result
            jq_command = [
                'jq',
                '-r',
                '.results.utterances[] | "[Speaker:\(.speaker)] \(.transcript)"'
            ]

            # Run jq command using subprocess and pipe the result from curl to jq
            jq_result = subprocess.run(
                jq_command, input=result.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if jq_result.returncode != 0:
                print(f"Error: {jq_result.stderr}")
                return None, None, None, None, None, None, None, None
            else:
                # Print the processed result
                print(jq_result.stdout)
                transcript = jq_result.stdout

        logging.info(f"Transcription completed for call ID: {
                     document['callId']}")

    except Exception as e:
        error_message = f"An error occurred processing the call ({document['callId']}): {
            str(e)} while transcribing the audio"
        notify(error_message)
        logging.error(error_message)
        return None, None, None, None, None, None, None, None

    os.remove(audio_filename)
    logging.info(f"Removed audio file {audio_filename}")

    try:
        chat = model.start_chat(history=[])
        logging.info(f"Started chat session for call ID: {document['callId']}")

        chat.send_message(
            f"I'll give you a call transcript between the user {user} and the sarathi {
                expert}. You have to correctly identify which Speaker is the User and which Speaker is the Sarathi (Generally Sarathi will be the one who ask the User questions about their routine and how they are doing. Also you can identify which speaker is Sarathi by their name). The user and sarathi connected via a website called 'Sukoon.Love', a platform for people to have conversations and seek guidance from Sarathis. Analyze the transcript and answer the questions I ask accordingly."
        ).resolve()
        logging.info(
            f"Sent initial message to chat model for call ID: {
                document['callId']}"
        )

        chat.send_message(
            transcript + "\n This is the transcript for the call").resolve()
        logging.info(f"Sent transcript to chat model for call ID: {
                     document['callId']}"
                     )

        chat.send_message(
            """
            Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harassment, discrimination,religious 
            or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong,  with the confidence score between 0 to 1.  Please be strict in analysing and give correct data only
            """
        ).resolve()
        logging.info(
            f"Requested analysis of inappropriate content for call ID: {
                document['callId']}"
        )

        summary = chat.last.text.replace("*", " ")

        if "All good" in summary:

            chat.send_message(
                """
                Calculate probability of the user calling back only on the basis of conversation don't include platform here, don't juudge on the basis of tonality just look for call back, dont calculate on the emotions, Be sure in giving data don't say may be, give TRUE or FALSE, and explanation in 10 words.
                """
            ).resolve()
            logging.info(
                f"Requested probability of callback for call ID: {
                    document['callId']}"
            )
            user_callback = chat.last.text.replace("*", " ")
            logging.info(
                f"No inappropriate content found for call ID: {
                    document['callId']}"
            )

            chat.send_message(
                "Summarize the transcript, with the confidence score between 0 to 1").resolve()
            logging.info(
                f"Requested transcript summary for call ID: {
                    document['callId']}"
            )
            summary = chat.last.text.replace("*", " ")

            chat.send_message(
                "Give me feedback for the saarthi(sarathi, agent,expert,experts)").resolve()
            logging.info(
                f"Requested saarthi feedback for call ID: {document['callId']}"
            )
            saarthi_feedback = chat.last.text.replace("*", " ")

            if user_calls == 1:

                with open("guidelines.txt", "r", encoding="utf-8") as file:
                    guidelines = file.read()
            else:
                with open("guidelines2.txt", "r", encoding="utf-8") as file:
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
                with the confidence score between 0 to 1,
                 Please be strict in analysing and give correct data only
                """
            ).resolve()
            logging.info(
                f"Requested detailed conversation analysis for call ID: {
                    document['callId']}"
            )
            conversation_score_details = chat.last.text.replace("*", " ")

            chat.send_message("Give me a total score out of 100").resolve()
            logging.info(f"Requested total score for call ID: {
                         document['callId']}")
            conversation_score = chat.last.text
            conversation_score = re.findall(
                r"\b(?:\d{2}|100)\b", conversation_score)
            try:
                conversation_score = int(conversation_score[0])
                conversation_score = conversation_score / 20
                logging.info(
                    f"Calculated total score: {
                        conversation_score} for call ID: {document['callId']}"
                )
            except Exception as e:
                logging.error(f"Error calculating total score: {str(e)}")
                conversation_score = 0

            # if persona != "None":
            #     chat.send_message(
            #         f"""
            #         This is the user persona derived from previous call transcripts of the user.
            #         User Persona: {persona}

            #         Remember this and answer the next question accordingly.
            #         with the confidence score between 0 to 1
            #         """
            #     ).resolve()
            #     logging.info(
            #         f"Sent user persona to chat model for call ID: {document['callId']}"
            #     )
            # else:
            #     logging.info(
            #         f"No previous user persona provided for call ID: {document['callId']}"
            #     )
            with open("topics.txt", "r", encoding="utf-8") as file:
                topics = file.read()

            chat.send_message(f"Identify the topics they are talking about from the {
                              topics}").resolve()
            logging.info(
                f"Requested topic identification for call ID: {
                    document['callId']}"
            )
            topics = chat.last.text.replace("*", " ")

            chat.send_message(
                """
                Context: Generate a user persona from the transcript provided above. Use only the lines which the User aid not the sarathi from the transcript to generate this persona. The persona should encompass demographics, psychographics, and personality traits based on the conversation. Specify the reason also for every field.

                a. User Demographics:
                2. Gender:
                3. Ethnicity:
                4. Education:
                5. Marital Status Choose one(Single/Married/Widow/Widower/Divorced/Unmarried):
                6. Income:
                7. Living Status Choose one(Stays alone/Stays with spouse only/Stays with spouse and kids/Stays with kids (no spouse)/Has parents staying with them ):
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
                with the confidence score between 0 to 1,
                 Please be strict in analysing and give correct data only
                """
            ).resolve()
            logging.info(
                f"Requested user persona analysis for call ID: {
                    document['callId']}"
            )
            customer_persona = chat.last.text.replace("*", " ")

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
                f"Inappropriate content found for call ID: {
                    document['callId']}"
            )
            return None, None, None, None, None, None, None, None

    except Exception as e:
        notify(f"An error occurred on process_call_recording:{str(e)}")
        logging.error(
            f"An error occurred during chat processing for call ID: {
                document['callId']}: {str(e)}"
        )
        return None, None, None, None, None, None, None, None
