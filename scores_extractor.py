from pymongo import MongoClient
from bson import ObjectId
import re

client = MongoClient(
    "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["test"]
calls_collection = db["calls"]
experts_collection = db["experts"]


def calls_scores_extractor():
    calls = calls_collection.find()
    subheading_to_key = {
        "Opening Greeting": "openingGreeting",
        "Tonality": "tonality",
        "Time Split Between Saarthi and User": "timeSplit",
        "User Sentiment": "userSentiment",
        "Flow of Conversation": "flow",
        "Time Spent on Call": "timeSpent",
        "Probability of Calling Back": "probability",
        "Closing Greeting": "closingGreeting",
    }
    for call in calls:
        if call.get("Score Breakup"):
            fractions = re.findall(
                r"([a-zA-Z\s]+)\s+\((\d+)/\d+\)", call["Score Breakup"]
            )
            for fraction in fractions:
                subheading = fraction[0].strip()
                if subheading in subheading_to_key:
                    key = subheading_to_key[subheading]
                    value = int(fraction[1])
                    update_query = {"$set": {key: value}}
                    calls_collection.update_one({"_id": call["_id"]}, update_query)


def calculate_average_scores():
    calls_scores_extractor()
    experts_scores = {}
    for call in calls_collection.find():
        expert_id = call["expert"]
        expert_id = ObjectId(expert_id)
        if expert_id not in experts_scores:
            experts_scores[expert_id] = {
                "openingGreeting": [],
                "tonality": [],
                "timeSplit": [],
                "userSentiment": [],
                "flow": [],
                "timeSpent": [],
                "probability": [],
                "closingGreeting": [],
            }
        if call.get("openingGreeting"):
            experts_scores[expert_id]["openingGreeting"].append(call["openingGreeting"])
        if call.get("tonality"):
            experts_scores[expert_id]["tonality"].append(call["tonality"])
        if call.get("timeSplit"):
            experts_scores[expert_id]["timeSplit"].append(call["timeSplit"])
        if call.get("userSentiment"):
            experts_scores[expert_id]["userSentiment"].append(call["userSentiment"])
        if call.get("flow"):
            experts_scores[expert_id]["flow"].append(call["flow"])
        if call.get("timeSpent"):
            experts_scores[expert_id]["timeSpent"].append(call["timeSpent"])
        if call.get("probability"):
            experts_scores[expert_id]["probability"].append(call["probability"])
        if call.get("closingGreeting"):
            experts_scores[expert_id]["closingGreeting"].append(call["closingGreeting"])
    for expert_id, scores in experts_scores.items():
        total_openingGreeting = len(scores["openingGreeting"])
        total_tonality = len(scores["tonality"])
        total_timeSplit = len(scores["timeSplit"])
        total_userSentiment = len(scores["userSentiment"])
        total_flow = len(scores["flow"])
        total_timeSpent = len(scores["timeSpent"])
        total_probability = len(scores["probability"])
        total_closingGreeting = len(scores["closingGreeting"])
        average_scores = {
            "openingGreeting": (
                round(sum(scores["openingGreeting"]) / total_openingGreeting, 2)
                if total_openingGreeting != 0
                else 0
            ),
            "tonality": (
                round(sum(scores["tonality"]) / total_tonality, 2)
                if total_tonality != 0
                else 0
            ),
            "timeSplit": (
                round(sum(scores["timeSplit"]) / total_timeSplit, 2)
                if total_timeSplit != 0
                else 0
            ),
            "userSentiment": (
                round(sum(scores["userSentiment"]) / total_userSentiment, 2)
                if total_userSentiment != 0
                else 0
            ),
            "flow": (
                round(sum(scores["flow"]) / total_flow, 2) if total_flow != 0 else 0
            ),
            "timeSpent": (
                round(sum(scores["timeSpent"]) / total_timeSpent, 2)
                if total_timeSpent != 0
                else 0
            ),
            "probability": (
                round(sum(scores["probability"]) / total_probability, 2)
                if total_probability != 0
                else 0
            ),
            "closingGreeting": (
                round(sum(scores["closingGreeting"]) / total_closingGreeting, 2)
                if total_closingGreeting != 0
                else 0
            ),
        }
        experts_collection.update_one({"_id": expert_id}, {"$set": average_scores})
