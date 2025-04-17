import json
import os
import requests

from modules.bearer_fetch import fetch_bearer_using_selenium
from modules import fish_api
from modules.utils.text_splicer import split_text_by_period

import logging

"""
TODO:
- Make a class in fish_api.py to handle all API requests.(done)
- Use session for requests to avoid re-authentication for every request.(done)
- Add error handling for API requests.
"""


logging.basicConfig(filename="runtime.log",level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    print("config.json not found. Please create a config.json file.")
    exit(1)

BEARER_TOKEN = config.get("BearerToken")
USER_ID = None
VOICE_NAME = config.get("Voice_Name")
INPUT_FOLDER = 'inputFiles'
DOWNLOAD_FOLDER = 'outputFiles'
characterLimitPerChunk = config.get("characterLimitPerChunk")

fish_self_api = "https://api.fish.audio/user/self"

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

fish_api_calls = fish_api.fish_api_calls(token=BEARER_TOKEN)

response = requests.get(fish_self_api, headers=headers)
if response.status_code == 200:
    data = response.json()
    # print(data)
    if data["banned"]: # Its a True False value
        print("Your account is banned.")
        print(f"Banned reason: '{data['banned_reason']}'")
        exit(1)
    USER_ID = data['_id']
    print(f"User ID: {USER_ID}")
    print(f"Username: {data['nickname']}")
    print(f"Email: {data['email']}")
    fish_api_calls.set_bearer_token(BEARER_TOKEN)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
    print("Fetching Bearer token using Selenium...")
    email = config['Email']
    password = config['Password']
    BEARER_TOKEN = fetch_bearer_using_selenium(email, password)
    config["BearerToken"] = BEARER_TOKEN
    logging.info(f"Bearer token fetched using Selenium: {BEARER_TOKEN}")
    
    # Update the token in the fish_api_calls module
    fish_api_calls.set_bearer_token(BEARER_TOKEN)
    
    # Update the headers in the current script
    headers['Authorization'] = f'Bearer {BEARER_TOKEN}'
    
    # Save the updated token to the config file
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("Bearer token updated in config.json.")
    input("Please run the script again.")
    exit(1)


if __name__ == "__main__":
    
    voice_id = fish_api_calls.get_voice_id(VOICE_NAME)
    print(f"Voice ID: {voice_id}")
    logging.info(f"Voice ID: {voice_id}")

    input_projects_path = os.path.join(os.getcwd(), INPUT_FOLDER)
    # input_projects = os.listdir(INPUT_FOLDER)    
    folders = [f for f in os.listdir(input_projects_path) if os.path.isdir(os.path.join(input_projects_path, f))]

    for folder_name in folders:
        current_credit_balance = int(fish_api_calls.get_current_credit_balance(USER_ID))
        print(f"Current Credit Balance: {current_credit_balance}")

        logging.info(f"Current Credit Balance: {current_credit_balance}")

        if current_credit_balance < 10000:
            print(f"Low credits: {current_credit_balance} credits left.")
            logging.info(f"Low credits: {current_credit_balance} credits left.")
            # logging.info("Low credits")
            input("Press Enter to continue or press (Ctrl+c) to stop...")
        
        folder_path = os.path.join(input_projects_path, folder_name)
        print(f"Processing folder: {folder_name}")
        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        studio_project_id = fish_api_calls.create_studio_project(voice_id, "speech-1.5", folder_name[:10])
        logging.info(f"Studio Project ID: {studio_project_id} with name: {folder_name[:10]}")

        print(f"Studio Project ID: {studio_project_id}")

        download_links = []
        for file_name in files:
            # Create one chapter for each file
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_name}")
            print()
            logging.info(f"Processing file: {file_name}")
            chapter_id = fish_api_calls.create_chapter(studio_project_id, file_name[:20])
            logging.info(f"Chapter ID: {chapter_id} with name: {file_name[:20]}")

            print(f"Chapter ID: {chapter_id}")
            text_chunks = split_text_by_period(file_path, characterLimitPerChunk)

            no_of_chunks = len(text_chunks)
            logging.info(f"Number of chunks: {no_of_chunks}")
            # block_ids = []
            for i, chunk in enumerate(text_chunks):
                print(f"\rInserting block {i + 1}/{no_of_chunks}...",end="\r")
                fish_api_calls.insert_text_block(content=chunk, chapter_id=chapter_id, studio_id=studio_project_id, voice_id=voice_id)
            print()
            blocks = fish_api_calls.get_chapter_blocks(studio_project_id, chapter_id)

            if len(blocks) == no_of_chunks:
                print(f"All {no_of_chunks} blocks inserted successfully.")
            
            print("Exporting chapter...")
            download_link = fish_api_calls.export_chapter(studio_project_id, chapter_id)
            print(f"Download link: {download_link}")
            logging.info(f"Download link: {download_link}")
            download_links.append(download_link)

        print(f"All chapters exported successfully. Downloading audio files for project {folder_name}...")
        logging.info(f"All chapters exported successfully. Downloading audio files...")

        for download_link in download_links:
            print(f"Downloading from link: {download_link}")
            # Download the audio file
            response = requests.get(download_link, headers=headers)
            if response.status_code == 200:
                audio_file_name = download_link.split("/")[-1]
                if not os.path.exists(os.path.join(DOWNLOAD_FOLDER, folder_name)):
                    os.makedirs(os.path.join(DOWNLOAD_FOLDER, folder_name))
                audio_file_path = os.path.join(DOWNLOAD_FOLDER, folder_name, audio_file_name)
                with open(audio_file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {audio_file_name}")
            else:
                print(f"Error downloading file: {response.status_code}")
