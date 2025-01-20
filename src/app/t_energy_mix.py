import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.environ['ENERGY_MIX_API_KEY']

def get_power_breakdown(zone):
    url = "https://api.electricitymap.org/v3/power-breakdown/history"
    headers = {
        "auth-token": key
    }
    params = {
        "zone": zone
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "history" in data and len(data["history"]) > 0:
            latest_entry = data["history"][-1]  # Get the latest entry
            filtered_entry = {
                "zone": zone,
                "datetime": latest_entry.get("datetime"),
                "powerConsumptionBreakdown": latest_entry.get("powerConsumptionBreakdown"),
                "fossilFreePercentage": latest_entry.get("fossilFreePercentage"),
                "renewablePercentage": latest_entry.get("renewablePercentage")
            }
            return filtered_entry
        else:
            print("No history data available.")
            return None
    else:
        print(f"An error occurred: {response.status_code} - {response.text}")
        return None

# Example usage
zone = "FR"  # Replace with the desired zone
latest_data = get_power_breakdown(zone)
if latest_data:
    print(latest_data)