from config import experts_collection
from datetime import datetime, timedelta
from notify import notify
import time
import pytz


def job():
    query = {"status": "online"}
    update = {"$set": {"status": "offline"}}
    result = experts_collection.update_many(query, update)
    if result.modified_count > 0:
        datetime_now = datetime.now(pytz.timezone("Asia/Kolkata"))
        notify(
            f"Testing... All Saarthis are offline now at {datetime_now.hour}:{datetime_now.minute}"
        )


while True:
    current_time = datetime.now(pytz.timezone("Asia/Kolkata"))
    target_time = current_time.replace(hour=1, minute=35, second=0, microsecond=0)
    if current_time > target_time:
        target_time = target_time + timedelta(days=1)
    sleep_duration = (target_time - current_time).total_seconds()
    time.sleep(sleep_duration)
    job()
