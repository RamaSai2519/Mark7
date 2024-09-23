from config import main_lambda_url as url
import requests
import json


def updater(expert_id: str, expert_number: str) -> None:
    payload = json.dumps({
        "expert_id": "6604675f42f04a057fa20e09",
        "expert_number": "7596938218"
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
