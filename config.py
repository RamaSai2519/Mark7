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
fcm_tokens_collection = db["fcm_tokens"]
errorlog_collection = db["errorlogs"]

retry_interval_seconds = 43200
client = OpenAI(api_key="sk-proj-aKKDe91pGa2k6HMxYksiT3BlbkFJfijdRZELYUustkm8biLd")
genai.configure(api_key="AIzaSyC7GliarMdf_jCp6SbKpfzjGwW1IdgFKws")
model = genai.GenerativeModel("gemini-pro")
