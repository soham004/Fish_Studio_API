import json
import os
import requests

from modules.bearer_fetch import fetch_bearer_using_selenium
from modules import fish_api

if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    print("config.json not found. Please create a config.json file.")
    exit(1)

BEARER_TOKEN = config.get("BearerToken")
USER_ID = None
VOICE_NAME = config.get("Voice_Name")

fish_self_api = "https://api.fish.audio/user/self"

headers={'accept': 'application/json', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site'}

headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.6',
    'Origin': 'https://fish.audio',
    'Priority': 'u=1, i',
    'Referer': 'https://fish.audio/',
    'Sec-Ch-Ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Gpc': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

response = requests.get(fish_self_api, headers=headers)
if response.status_code == 200:
    data = response.json()
    # print(data)
    USER_ID = data['_id']
    print(f"User ID: {USER_ID}")
    print(f"Username: {data['nickname']}")
    print(f"Email: {data['email']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
    print("Fetching Bearer token using Selenium...")
    email = config['Email']
    password = config['Password']
    BEARER_TOKEN = fetch_bearer_using_selenium(email, password)
    config["BearerToken"] = BEARER_TOKEN
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# fish_api.BEARER_TOKEN = BEARER_TOKEN
if __name__ == "__main__":
    fish_api.set_bearer_token(BEARER_TOKEN)
    current_credit_balance = int(fish_api.get_current_credit_balance(USER_ID))
    print(f"Current Credit Balance: {current_credit_balance}")

    if current_credit_balance < 0:
        print("Insufficient credits")

    voice_id = fish_api.get_voice_id(VOICE_NAME)
    print(f"Voice ID: {voice_id}")

    studio_project_id = fish_api.create_studio_project(voice_id, "speech-1.5", "Testing Back")
    print(f"Studio Project ID: {studio_project_id}")

    chapter_id = fish_api.create_chapter(studio_project_id, "Testing Chapter")
    print(f"Chapter ID: {chapter_id}")
