import google.generativeai as genai
import logging
import os
from pymongo import MongoClient
from openai import OpenAI
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
client = OpenAI(
    api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")

# Configure the generative AI with the API key
genai.configure(api_key=os.getenv("GEMNAI_KEY"))

# Initialize the generative model
model = genai.GenerativeModel("gemini-pro")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
