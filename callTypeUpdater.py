from config import schedules_collection, calls_collection
from datetime import timedelta, datetime
from time import sleep

# Find all schedules
schedules = list(schedules_collection.find({"status": "pending"}))

while True:
    for schedule in schedules:
        schedule_user = schedule["user"]
        schedule_expert = schedule["expert"]

        # Adjust schedule time to match call time (assuming your schedule time is in IST and call time is in UTC)
        schedule_time = schedule["datetime"] - timedelta(hours=5, minutes=30)

        # Find calls for the same user and expert within a small time window around the schedule time
        calls = list(
            calls_collection.find(
                {
                    "user": schedule_user,
                    "expert": schedule_expert,
                    "initiatedTime": {
                        "$gte": schedule_time - timedelta(minutes=1),
                        "$lte": schedule_time + timedelta(minutes=1),
                    },
                }
            )
        )

        if calls:
            schedules_collection.update_one(
                {"_id": schedule["_id"]}, {"$set": {"status": "completed"}}
            )
            for call in calls:
                # Update the call type in the database
                call_type = "scheduled"
                calls_collection.update_one(
                    {"_id": call["_id"]}, {"$set": {"type": call_type}}
                )
                print(
                    f"Updated call type for call initiated at {call['initiatedTime']}"
                )
        else:
            if (schedule_time + timedelta(hours=5, minutes=30)) < datetime.now():
                print(schedule_time, datetime.now())
                schedules_collection.update_one(
                    {"_id": schedule["_id"]}, {"$set": {"status": "missed"}}
                )
            else:
                schedules_collection.update_one(
                    {"_id": schedule["_id"]}, {"$set": {"status": "pending"}}
                )

    sleep(30 * 60)  # Check every 30 minutes
