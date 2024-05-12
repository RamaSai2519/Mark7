from config import *
import requests
import time

def notify(message):
    fcm_url = "https://fcm.googleapis.com/fcm/send"
    server_key = "AAAAM5jkbNg:APA91bG80zQ8CzD1AeQmV45YT4yWuwSgJ5VwvyLrNynAJBk4AcyCb6vbCSGlIQeQFPAndS0TbXrgEL8HFYQq4DMXmSoJ4ek7nFcCwOEDq3Oi5Or_SibSpywYFrnolM4LSxpRkVeiYGDv"
    tokens = list(fcm_tokens_collection.find())
    for token in tokens:
        payload = {
            "to": token["token"],
            "notification": {"title": "Notification", "body": message},
        }
        headers = {
            "Authorization": "key=" + server_key,
            "Content-Type": "application/json",
        }
        response = requests.post(fcm_url, json=payload, headers=headers)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        errorlog_collection.insert_one({"message": message, "time": current_time})
    if response.status_code == 200:
        pass
    else:
        print("Failed to send notification:", response.text)
