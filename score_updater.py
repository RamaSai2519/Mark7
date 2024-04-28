from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(
    "mongodb+srv://sukoon_user:Tcks8x7wblpLL9OA@cluster0.o7vywoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["test"]

calls_collection = db["calls"]
users_collection = db["users"]
experts_collection = db["experts"]


def updater():
    conversation_scores = {}
    for call in calls_collection.find():
        expert_id = str(call.get("expert"))
        if "Conversation Score" not in call:
            continue
        score = call.get("Conversation Score", 0)
        conversation_scores.setdefault(expert_id, []).append(score)

    average_conversation_scores = {}
    for expert_id, scores in conversation_scores.items():
        average_score = sum(scores) / len(scores) if scores else 0
        average_conversation_scores[expert_id] = average_score
        average_score = round(average_score, 1)
        experts_collection.update_one(
            {"_id": ObjectId(expert_id)}, {"$set": {"score": average_score}}
        )
        # print(f"{expert_id}: {average_score}")

    total_users_per_expert = {}
    user_calls_to_experts = {}

    calls = calls_collection.find()

    expert_names = {}
    for expert in experts_collection.find():
        expert_names[str(expert.get("_id"))] = expert.get("name")

    user_names = {}
    for user in users_collection.find():
        user_names[str(user.get("_id"))] = user.get("name")

    excluded_users = [
        "6604618e42f04a057fa20cbb",
        "6604a57ad0a5b997c4121881",
        "660acafe9f28ee9c2c00762c",
        "660e5f213a2d66e7354e714c",
        "6610ea948114085c8fe81961",
        "6612aa049100784ebd2f7f05",
        "6614b6a79100784ebd2f99f3",
        "661a21ce962c25df8c06332e",
        "661cf516962c25df8c0654a1",
        "661d3f3017982c74166f9c1d",
        "661f86e66ad8929bec29f568",
        "66211c0047d3fd0682c40afc",
    ]

    results_per_expert = []

    for call in calls:
        expert_id = str(call.get("expert"))
        user_id = str(call.get("user"))

        if user_id in excluded_users:
            continue

        total_users_per_expert.setdefault(expert_id, set()).add(user_id)

        user_calls_to_experts.setdefault(user_id, set()).add(expert_id)

    repeat_ratio_per_expert = {}
    for expert_id in total_users_per_expert.keys():
        total_users = len(total_users_per_expert[expert_id])
        repeat_users = 0
        for user_id in total_users_per_expert[expert_id]:
            if len(
                user_calls_to_experts.get(user_id, [])
            ) > 1 and expert_id in user_calls_to_experts.get(user_id, []):
                repeat_users += 1
        repeat_ratio_per_expert[expert_id] = (
            (repeat_users / total_users) * 100 if total_users != 0 else 0
        )

    for expert_id, repeat_ratio in repeat_ratio_per_expert.items():
        expert_name = expert_names.get(expert_id, "Unknown Expert")
        total_users = total_users_per_expert.get(expert_id, [])
        repeat_users = []
        for user_id in total_users:
            if len(
                user_calls_to_experts.get(user_id, [])
            ) > 1 and expert_id in user_calls_to_experts.get(user_id, []):
                repeat_users.append(user_names.get(user_id, "Unknown User"))


    for expert_id, repeat_ratio in repeat_ratio_per_expert.items():
        expert_name = expert_names.get(expert_id, "Unknown Expert")
        total_users = total_users_per_expert.get(expert_id, [])
        repeat_users = []
        for user_id in total_users:
            if len(
                user_calls_to_experts.get(user_id, [])
            ) > 1 and expert_id in user_calls_to_experts.get(user_id, []):
                repeat_users.append(user_names.get(user_id, "Unknown User"))
        repeat_ratio = int(repeat_ratio)
        result_sentence = f"{expert_id},{expert_name}: {repeat_ratio:.0f}%"
        results_per_expert.append(result_sentence)

    scores_per_expert = {}
    for expert in experts_collection.find():
        expert_id = str(expert.get("_id"))
        score = expert.get("score", 0) * 20
        scores_per_expert[expert_id] = score

    calls_per_expert = {}
    for call in calls_collection.find():
        expert_id = str(call.get("expert"))
        calls_per_expert[expert_id] = calls_per_expert.get(expert_id, 0) + 1

    total_calls = sum(calls_per_expert.values())

    final_scores = {}
    for expert_id in total_users_per_expert.keys():
        repeat_score = repeat_ratio_per_expert.get(expert_id, 0)
        repeat_score = int(repeat_score)
        try:
            experts_collection.update_one(
                {"_id": ObjectId(expert_id)}, {"$set": {"repeat_score": repeat_score}}
            )
        except Exception as e:
            print(f"Error updating expert: {e}")
        score = scores_per_expert.get(expert_id, 0)
        score = int(score)
        calls = calls_per_expert.get(expert_id, 0)
        normalized_calls = (calls / total_calls) * 100 if total_calls != 0 else 0
        normalized_calls = int(normalized_calls)

        final_score = (score + repeat_score + normalized_calls) / 3
        final_scores[expert_id] = final_score

    for expert_id, score in final_scores.items():
        score = int(score)
        calls = calls_per_expert.get(expert_id, 0)
        expert_name = expert_names.get(expert_id, "Unknown Expert")

        try:
            experts_collection.update_one(
                {"_id": ObjectId(expert_id)}, {"$set": {"total_score": score}}
            )
        except Exception as e:
            print(f"Error updating expert: {e}")


updater()