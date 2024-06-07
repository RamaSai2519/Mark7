import google.generativeai as genai
from pymongo import MongoClient
from openai import OpenAI

user_document = None
expert_document = None

client = MongoClient(
    "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["test"]
calls_collection = db["calls"]
users_collection = db["users"]
experts_collection = db["experts"]
fcm_tokens_collection = db["fcm_tokens"]
errorlog_collection = db["errorlogs"]
timings_collection = db["timings"]

retry_interval_seconds = 43200

# Initialize the OpenAI client with the API key
client = OpenAI(api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")

# Configure the generative AI with the API key
genai.configure(api_key="AIzaSyCVBseAUFeC5GcvRmKQxov4a1lh5qB3PxI")

# Initialize the generative model
model = genai.GenerativeModel("gemini-pro")

DEEPGRAM_API_KEY = "e461122ba4cef932ffd459baf5b54825f5ab3ff9"
