import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.environ['WEATHER_API_KEY']

def get_weather(location):
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "q": location,
        "days": 5,
        "key": key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"An error occurred: {response.status_code} - {response.text}")
        return None
    

