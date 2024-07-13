import logging
import os
from pymongo import MongoClient
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

user_document = None
expert_document = None

client = MongoClient(
    os.getenv("MONGO_KEY")
)

logging.info('APIKEY+'+os.getenv("MONGO_KEY"))

db = client["test"]
calls_collection = db["calls"]
users_collection = db["users"]
experts_collection = db["experts"]
fcm_tokens_collection = db["fcm_tokens"]
errorlog_collection = db["errorlogs"]
timings_collection = db["timings"]
callsmeta_collection = db["callsmeta"]
schedules_collection = db["schedules"]


# Initialize the OpenAI client with the API key
# client = OpenAI(api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")

# Configure the generative AI with the API key
# genai.configure(api_key=os.getenv("GEMNAI_KEY"))

# # Initialize the generative model
# model = genai.GenerativeModel("gemini-pro")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

open_ai_client = AzureOpenAI(
    azure_endpoint="https://sukoon-chat-2.openai.azure.com/",
    api_key="fef59650b89c417997e122739f41b5ca",
    api_version="2024-02-01"
)