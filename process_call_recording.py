from config import model, DEEPGRAM_API_KEY
from download_audio import download_audio
from notify import notify
import logging
import re
import os
import subprocess



def process_call_recording(document, user, expert, persona):
    audio_filename = f"{document['callId']}.mp3"
    logging.info(f"Starting process for call ID: {document['callId']}")

    download_audio(document, audio_filename)
    logging.info(
        f"Downloaded audio for call ID: {document['callId']} to {audio_filename}"
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
        result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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
            jq_result = subprocess.run(jq_command, input=result.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if jq_result.returncode != 0:
                print(f"Error: {jq_result.stderr}")
                return None, None, None, None, None, None, None, None
            else:
                # Print the processed result
                print(jq_result.stdout)
                transcript = jq_result.stdout
        # transcript = "[Speaker:0] Hello.\n[Speaker:1] Namaste.\n[Speaker:1] Sir,\n[Speaker:1] I am speaking from school.love.\n[Speaker:0] I was just testing if everything is going well.\n[Speaker:0] How are you?\n[Speaker:1] I am fine.\n[Speaker:0] You are good.\n[Speaker:0] How are the calls coming? Are the calls getting disconnected?\n[Speaker:1] Calls\n[Speaker:1] are coming less now but they are continuing.\n[Speaker:1] Because yesterday's\n[Speaker:1] call\n[Speaker:1] was\n[Speaker:1] about\n[Speaker:0] yesterday or day before yesterday. So it was more than one hour and it went well. Without any break, disturbance, clear. Okay, okay, okay. Good, good, good. Okay, calls will start coming. Now calls are coming less because we are making some changes.\n[Speaker:0] So\n[Speaker:0] don't worry about that. We'll start getting calls.\n[Speaker:0] Okay.\n[Speaker:0] Okay? Okay. And how's the weather here?\n[Speaker:1] The weather is good.\n[Speaker:0] Great. It's raining here Yes, it's raining\n[Speaker:0] Ok, you said you are from Bangalore?\n[Speaker:1] No, no, I am from Nashik, Nashik, Maharashtra\n[Speaker:1] Nashik, ok\n[Speaker:0] Near Mumbai, near Shirdi I know,\n[Speaker:0] I am from Bhopal,\n[Speaker:0] so when I come,\n[Speaker:0] I see\n[Speaker:0] Nasik,\n[Speaker:0] when I come from Bike Hike, I travel. Yes, yes.\n[Speaker:0] Ok. Actually, I want to talk to you for 5 minutes.\n[Speaker:0] 5 minutes, because a system runs after 5 minutes call.\n[Speaker:0] So,\n[Speaker:0] you are free now, right?\n[Speaker:0] Yes, I can. I want to talk about 2-3 aspects. Let's talk about Nasik Seher. And then I will talk about my personal life. So, based on that, there are some things that run\n[Speaker:1] I have to validate them properly\n[Speaker:0] Yes\n[Speaker:0] Ok\n[Speaker:0] So, now you tell me a little about Nasik\n[Speaker:0] Yes What is Nasik?\n[Speaker:1] First thing is that they were religious\n[Speaker:1] because\n[Speaker:1] the place\n[Speaker:1] where the statue was placed,\n[Speaker:1] Lord Ram lived there.\n[Speaker:1] So for this,\n[Speaker:1] the first\n[Speaker:1] religious place of Nashik is Godavari.\n[Speaker:1] Ram lived there and from here, Ravan kidnapped Sita.\n[Speaker:1] This is how it is said.\n[Speaker:1] And the second important thing is\n[Speaker:1] Shurpanakha,\n[Speaker:1] who was the sister of Ravana,\n[Speaker:1] her nose was\n[Speaker:1] cut off by Lakshmana.\n[Speaker:1] That is\n[Speaker:1] why the nose is called Nachik in Sanskrit.\n[Speaker:1] That is why the city's name is Nachik. And he has\n[Speaker:1] a Jyotirlingam\n[Speaker:1] called Brahmakeshwar\n[Speaker:1] where Gautam Rishi did tapasya raya\n[Speaker:1] and in north India there was Ganga and in south India there was no river\n[Speaker:1] so Gautam Rishi did Mahadev's tapasya raya and brought Ganga here. He told Mahadev to keep it in Jata\n[Speaker:1] because its pressure is too much.\n[Speaker:1] And after that,\n[Speaker:1] Mahadev's\n[Speaker:1] residence was here, so\n[Speaker:1] the Jyotirlingam of Tambakeshwar was\n[Speaker:1] made.\n[Speaker:0] This is the religious history. And that is why I made a comeback and called Jyotirlingam Maharaj Jyotirlingam this is my religious history\n[Speaker:1] and now Nashik\n[Speaker:1] is a\n[Speaker:1] good climate\n[Speaker:1] city\n[Speaker:1] where to live etc\n[Speaker:1] because there is not much heat and it is cold it is medium\n[Speaker:1] so it is a religious place and good to live\n[Speaker:1] I used to live in Kuala Lumpur, but after retirement I thought that\n[Speaker:1] Nashik is a good city to live in.\n[Speaker:1] So,\n[Speaker:1] tell us a little about yourself.\n[Speaker:0] Okay,\n[Speaker:0] I am from MP,\n[Speaker:0] there is a place called Bhopal. I am from Bhopal\n[Speaker:0] and I am married. I\n[Speaker:0] got married in 2020.\n[Speaker:0] I have two brothers.\n[Speaker:0] My parents live in Kanpur.\n[Speaker:0] My father is a physiotherapist.\n[Speaker:0] My mother is a housewife.\n[Speaker:0] I have been to Nashik.\n[Speaker:0] I\n[Speaker:0] have\n[Speaker:0] been to Nashik. I have brought my parents from Keshavar. Yeah.\n[Speaker:0] And my sister lives in Pune.\n[Speaker:0] Yeah.\n[Speaker:0] My sister\n[Speaker:0] lives in Pune.\n[Speaker:0] And\n[Speaker:0] I am a software engineer and I live in Bangalore.\n[Speaker:0] I have worked\n[Speaker:0] with point switch and other companies.\n[Speaker:0] My primary interest is in software\n[Speaker:0] and a little bit in spirituality.\n[Speaker:0] These are my two primary interests.\n[Speaker:0] And that's all about me.\n[Speaker:0] Yes.\n[Speaker:0] Yes. And how will Nasik\n[Speaker:0] reach if someone is coming from Bangalore?\n[Speaker:0] So how can they come?\n[Speaker:1] There is a train from Bangalore,\n[Speaker:1] but\n[Speaker:1] they can also come by flight because Nasik has an airport as well. Okay.\n[Speaker:1] Mumbai-Nashik\n[Speaker:1] flight is more than enough.\n[Speaker:1] Mumbai-Bangalore\n[Speaker:1] flight.\n[Speaker:1] You can come to Mumbai from Bangalore.\n[Speaker:1] From\n[Speaker:1] Mumbai,\n[Speaker:1] you\n[Speaker:1] can\n[Speaker:1] reach Nashik comfortably in a 3-hour journey.\n[Speaker:1] Okay. And Nashik has good food and accommodation.\n[Speaker:1] We have all types of hotels.\n[Speaker:1] Food is also available. We have all varieties.\n[Speaker:1] And for new people,\n[Speaker:1] we\n[Speaker:1] have a wine capital here.\n[Speaker:1] We have wineries here.\n[Speaker:1] So, it is good.\n[Speaker:0] And secondly, can you come from Pune?\n[Speaker:0] Because from Bangalore to Pune is a long way\n[Speaker:1] correct correct from Pune\n[Speaker:1] to\n[Speaker:1] Bangalore\n[Speaker:1] I think it is 1500 km but from Pune it is just 200 KM\n[Speaker:1] and from Pudhe,\n[Speaker:1] there is a continuous bus\n[Speaker:1] every 30 minutes\n[Speaker:1] and it takes around 5 hours,\n[Speaker:1] if there is a traffic jam then it takes 5 hours if you come by bus\n[Speaker:1] it takes 4 hours\n[Speaker:1] the road is good this is a big highway\n[Speaker:1] big highway means 4 lane highway\n[Speaker:0] yes\n[Speaker:0] ok sir\n[Speaker:0] it was nice talking to you\n[Speaker:0] yes\n[Speaker:0] ok thank you have a nice day Okay, okay, okay. Okay, sir. I really enjoyed talking to you. Yeah, not a problem. Okay, thank you. Thank you, sir. Have a nice day.\n"

        logging.info(f"Transcription completed for call ID: {document['callId']}")

    except Exception as e:
        error_message = f"An error occurred processing the call ({document['callId']}): {str(e)} while transcribing the audio"
        notify(error_message)
        logging.error(error_message)
        return None, None, None, None, None, None, None, None

    os.remove(audio_filename)
    logging.info(f"Removed audio file {audio_filename}")

    chat = model.start_chat(history=[])
    logging.info(f"Started chat session for call ID: {document['callId']}")

    try:
        chat.send_message(
            f"I'll give you a call transcript between the user {user} and the sarathi {expert}. You have to correctly identify which Speaker is the User and which Speaker is the Sarathi (Generally Sarathi will be the one who ask the User questions about their routine and how they are doing. Also you can identify which speaker is Sarathi by their name). The user and sarathi connected via a website called 'Sukoon.Love', a platform for people to have conversations and seek guidance from Sarathis. Analyze the transcript and answer the questions I ask accordingly."
        ).resolve()
        logging.info(
            f"Sent initial message to chat model for call ID: {document['callId']}"
        )

        chat.send_message(transcript + "\n This is the transcript for the call").resolve()
        logging.info(f"Sent transcript to chat model for call ID: {document['callId']}")

        chat.send_message(
            """
            Analyze the transcript and flag any instances of inappropriate language or behavior. Detect any offensive language, insults, harassment, discrimination,religious 
            or any other form of inappropriate communication. Just say "All good" if nothing is wrong or give a summary of flagged content if found anything wrong,  with the confidence score between 0 to 1.  Please be strict in analysing and give correct data only
            """
        ).resolve()
        logging.info(
            f"Requested analysis of inappropriate content for call ID: {document['callId']}"
        )

        summary = chat.last.text.replace("*", " ")

        if "All good" in summary:

            chat.send_message(
                """
                Calculate probability of the user calling back only on the basis of conversation don't include platform here, don't juudge on the basis of tonality just look for call back, dont calculate on the emotions, Be sure in giving data don't say may be, give TRUE or FALSE, and explanation in 10 words.
                """
            ).resolve()
            logging.info(
                f"Requested probability of callback for call ID: {document['callId']}"
            )
            user_callback = chat.last.text.replace("*", " ")
            logging.info(
                f"No inappropriate content found for call ID: {document['callId']}"
            )

            chat.send_message("Summarize the transcript, with the confidence score between 0 to 1").resolve()
            logging.info(
                f"Requested transcript summary for call ID: {document['callId']}"
            )
            summary = chat.last.text.replace("*", " ")

            chat.send_message("Give me feedback for the saarthi(sarathi, agent,expert,experts)").resolve()
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
                with the confidence score between 0 to 1,
                 Please be strict in analysing and give correct data only
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

            chat.send_message(
                """
                Context: Generate a user persona from the transcript provided above. Use only the lines which the User aid not the sarathi from the transcript to generate this persona. The persona should encompass demographics, psychographics, and personality traits based on the conversation. Specify the reason also for every field.

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
                with the confidence score between 0 to 1,
                 Please be strict in analysing and give correct data only
                """
            ).resolve()
            logging.info(
                f"Requested user persona analysis for call ID: {document['callId']}"
            )
            customer_persona = chat.last.text.replace("*", " ")

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
        return None, None, None, None, None, None, None, None
