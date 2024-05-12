from config import calls_collection

# Function to extract and sum the score fractions from a call document
def sum_score_fractions(call_document):
    call_id = call_document.get("callId")
    score_breakup = call_document.get("Score Breakup")
    total_score = 0
    fractions = []
    for line in score_breakup.split("\n"):
        if "/" in line:
            parts = line.split("/")
            if len(parts) >= 2:
                score_part = parts[0].split("(")[-1].strip()
                try:
                    score = int(score_part)
                    fractions.append(score)
                    total_score += score
                except ValueError:
                    pass
    return call_id, fractions, total_score


def corrector(id):
    # Find all calls with 'Score Breakup'
    call = calls_collection.find_one({"callId": id})

    # Iterate over each call and calculate the total score
    call_scores = {}
    call_id, fractions, total_score = sum_score_fractions(call)
    call_scores[call_id] = {"fractions": fractions, "total_score": total_score}

    # Iterate over each call and update the Conversation Score
    for call_id, scores in call_scores.items():
        score = scores["total_score"] / 20
        calls_collection.update_one(
            {"callId": call_id}, {"$set": {"Conversation Score": score}}
        )
