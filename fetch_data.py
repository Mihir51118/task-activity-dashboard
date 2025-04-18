import requests
import json
import os
from datetime import datetime, timedelta

# Automatically fetch data for the last 1 day
FROM_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
TO_DATE   = datetime.now().strftime("%Y-%m-%d")

# API URL with dynamic date range
API_URL = f"http://startupworld.in/Version1/get_task_activity.php?from_date={FROM_DATE}&to_date={TO_DATE}"

# Save location
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "task_data.json")

def fetch_task_data():
    try:
        print(f"📡 Fetching task data from {FROM_DATE} to {TO_DATE}...")

        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()  # Raise for HTTP errors (4xx, 5xx)

        response_data = response.json()
        task_data = response_data.get("data", [])

        if not task_data:
            print("⚠️ No task data returned by the API.")
            return

        # Ensure data folder exists
        os.makedirs(DATA_DIR, exist_ok=True)

        # Save only the "data" portion into the file
        with open(DATA_FILE, "w") as f:
            json.dump(task_data, f, indent=2)

        print(f"✅ Task data saved to '{DATA_FILE}'!")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request error occurred: {req_err}")
    except Exception as err:
        print(f"❌ Unexpected error: {err}")

# Run when executed directly
if __name__ == "__main__":
    fetch_task_data()
