import requests
import json
import os
from datetime import datetime

# Set your date range
FROM_DATE = "2024-01-01"
TO_DATE = "2024-01-31"

# API URL
API_URL = f"http://startupworld.in/Version1/get_task_activity.php?from_date={FROM_DATE}&to_date={TO_DATE}"

# Folder where data will be saved
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "task_data.json")

def fetch_task_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()  # Raises an error for 4xx/5xx codes
        
        data = response.json()
        
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Save the data
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Data fetched and saved successfully at '{DATA_FILE}'!")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request error occurred: {req_err}")
    except Exception as err:
        print(f"❌ An unexpected error occurred: {err}")

if __name__ == "__main__":
    fetch_task_data()
