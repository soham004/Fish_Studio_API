import json
import os
import requests
import time
import random
from modules.bearer_fetch import fetch_bearer_using_selenium
from modules import fish_api
from modules.utils.text_tools import *
from modules.utils.notifier import notify

import logging

"""
TODO:
- Make a class in fish_api.py to handle all API requests.(done)
- Use session for requests to avoid re-authentication for every request.(done)
- Add error handling for API requests. 
- Add chapter deletion in case of chunk upload failure and retry the upload.(done)
- Inform user if selected voice is not available.(done)
- Remove all the hard exits and use exceptions instead.
- Add chapter grouping for exporting multiple chapters at a time
"""


logging.basicConfig(filename="runtime.log",level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    print("config.json not found. Please create a config.json file.")
    print("Example config.json:")
    print(
"""
{
    "BearerToken": "",
    "Email": "email@domain.com",
    "Password": "Password",
    "characterLimitPerChunk": 500,
    "Voice_Name": "Very Original Name"
}
""")
    exit(1)

bearer_token = config.get("BearerToken")
USER_ID = None
VOICE_NAME = config.get("Voice_Name")
INPUT_FOLDER = 'inputFiles'
DOWNLOAD_FOLDER = 'outputFiles'
characterLimitPerChunk = config.get("characterLimitPerChunk")

fish_self_api = "https://api.fish.audio/user/self"

headers = {
    'Authorization': f'Bearer {bearer_token}',
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

def create_chapter_and_export(file_name:str, file_path:str,studio_project_id:str, voice_id:str) -> tuple:
    """
    It retuns a tuple of chapter_id and download_link.
    """
    chapter_id = fish_api_calls.create_chapter(studio_project_id, file_name[:20])
    logging.info(f"Chapter ID: {chapter_id} with name: {file_name[:20]}")

    print(f"Chapter {file_name[:20]} ID: {chapter_id}")
    text_chunks = split_text_by_period(file_path, characterLimitPerChunk)

    no_of_chunks = len(text_chunks)
    logging.info(f"Number of chunks: {no_of_chunks}")
    # block_ids = []
    for i, chunk in enumerate(text_chunks):
        print(f"\rInserting block {i + 1}/{no_of_chunks}...",end="\r")
        time.sleep(random.uniform(0,1))  # Random sleep between 0 and 1 seconds
        fish_api_calls.insert_text_block(content=chunk, chapter_id=chapter_id, studio_id=studio_project_id, voice_id=voice_id)
    print()
    time.sleep(random.randint(1, 5))  # Random sleep between 1 and 3 seconds
    blocks = fish_api_calls.get_chapter_blocks(studio_project_id, chapter_id)

    if len(blocks) == no_of_chunks:
        print(f"All {no_of_chunks} blocks inserted successfully.")
    
    print("Exporting chapter...")
    time.sleep(random.randint(1, 5))  # Random sleep between 1 and 3 seconds
    download_link = fish_api_calls.export_chapter(studio_project_id, chapter_id)

    return chapter_id, download_link

def download_from_link(download_link:str, folder_name:str, download_folder:str) -> None:
    print(f"Downloading from link: {download_link}")
    # Download the audio file
    time.sleep(random.randint(1, 5))  # Random sleep between 1 and 3 seconds
    response = requests.get(download_link, headers=headers)
    if response.status_code == 200:
        audio_file_name = download_link.split("/")[-1]

        cleaned_file_name = audio_file_name[22:] # Remove the first 22 characters i.e the timestamps
        if len(cleaned_file_name) > 4:
            audio_file_name = cleaned_file_name
        
        if not os.path.exists(os.path.join(download_folder, folder_name)):
            os.makedirs(os.path.join(download_folder, folder_name))
        audio_file_path = os.path.join(download_folder, folder_name, audio_file_name)
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {audio_file_name}")
    else:
        print(f"Error downloading file: {response.status_code}")

def display_failed_files(failed_files_dict_list):
    for failed_files_dict in failed_files_dict_list:
        if len(failed_files_dict["failed_files"]) > 0:
            print(f"Failed files in folder {failed_files_dict['folder_name']}: {failed_files_dict['failed_files']}")
            logging.info(f"Failed files in folder {failed_files_dict['folder_name']}: {failed_files_dict['failed_files']}")
        else:
            print(f"No failed files in folder {failed_files_dict['folder_name']}")
            logging.info(f"No failed files in folder {failed_files_dict['folder_name']}")

if __name__ == "__main__":
    
    with requests.get(fish_self_api, headers=headers) as response:
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
            # fish_api_calls.set_bearer_token(bearer_token)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            print("Fetching Bearer token using Selenium...")
            email = config['Email']
            password = config['Password']
            bearer_token = fetch_bearer_using_selenium(email, password)
            config["BearerToken"] = bearer_token
            logging.info(f"Bearer token fetched using Selenium: {bearer_token}")
            

            headers['Authorization'] = f'Bearer {bearer_token}'
            with requests.get(fish_self_api, headers=headers) as response:
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
                else:
                    print(f"Error: {response.status_code}")
                    print(response.text)
                    print("Bearer token is invalid. Please retry...")
                    exit(1)
            # Save the updated token to the config file
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            
            print("Bearer token updated in config.json.")


    fish_api_calls = fish_api.fish_api_calls(token=bearer_token)
    voice_id = fish_api_calls.get_voice_id(VOICE_NAME)
    if voice_id == None:
        print("The selected voice is not available")
        exit(1)
    print(f"Voice ID: {voice_id}")
    logging.info(f"Voice ID: {voice_id}")

    input_projects_path = os.path.join(os.getcwd(), INPUT_FOLDER)

    folders = [f for f in os.listdir(input_projects_path) if os.path.isdir(os.path.join(input_projects_path, f))]

    if len(folders) == 0:
        print(f"No folders found in {input_projects_path}.")
        logging.info(f"No folders found in {input_projects_path}.")
        exit(1)
    
    current_credit_balance = int(fish_api_calls.get_current_credit_balance(USER_ID))
    failed_files_dict_list = []

    for folder_name in folders:

        failed_files_dict = {
            "folder_name": folder_name,
            "failed_files": []
        }
        print("\n\n")
        folder_path = os.path.join(input_projects_path, folder_name)
        print(f"Processing folder: {folder_name}")
        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        print(f"Current Credit Balance: {current_credit_balance}")
        logging.info(f"Current Credit Balance: {current_credit_balance}")

        file_absolute_paths = [os.path.join(folder_path, f) for f in files]

        credits_required = get_utf8_bytes_size_from_files(file_absolute_paths)

        print(f"Credits required: {credits_required}")
        logging.info(f"Credits required: {credits_required}")

        if credits_required > current_credit_balance:
            print(f"Not enough credits to generate the whole project. Required: {credits_required}, Available: {current_credit_balance}")
            logging.info(f"Not enough credits. Required: {credits_required}, Available: {current_credit_balance}")
            continue

        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

        if len(files) == 0:
            print(f"No files found in {folder_name}.")
            logging.info(f"No files found in {folder_path}.")
            continue

        studio_project_id = fish_api_calls.create_studio_project(voice_id, "speech-1.5", folder_name[:10])
        logging.info(f"Studio Project ID: {studio_project_id} with name: {folder_name[:10]}")

        print(f"Studio Project ID: {studio_project_id}")
        download_link = None
        download_links = []

        for file_name in files:

            retries = 3
            for attempt in range(retries):
                print("\n")
                # Create one chapter for each file
                file_path = os.path.join(folder_path, file_name)
                print(f"Processing file: {file_name}")
                logging.info(f"Processing file: {file_name}")
                print()
                time.sleep(random.randint(1, 5))  # Random sleep between 1 and 5 seconds

                try:
                    chapter_id, download_link = create_chapter_and_export(file_name, file_path, studio_project_id, voice_id)
                    if download_link is None:
                        print(f"Error: Download link is None. Retrying...")
                        logging.error(f"Download link is None. Retrying...")
                        raise Exception("Download link is None.")
                    break
                except Exception as e:
                    print(f"Error exporting chapter: {e}")
                    logging.error(f"Error exporting chapter: {e}")
                    print(f"Deleting chapter...")
                    fish_api_calls.delete_chapter(studio_project_id, chapter_id)
                    retries -= 1
                    if retries == 0:
                        print(f"Failed to export chapter after {attempt + 1} attempts.")
                        logging.error(f"Failed to export chapter after {attempt + 1} attempts.")
                        break
                    else:
                        print(f"Retrying... ({retries} attempts left)")
                        logging.info(f"Retrying... ({retries} attempts left)")
                    
            if download_link is None:
                print(f"Download link is None. Skipping file: {file_name}")
                # failed_files.append(file_name)
                failed_files_dict["failed_files"].append(file_name)
                continue
            print(f"Download link: {download_link}")
            logging.info(f"Download link: {download_link}")
            download_links.append(download_link)
            chapter_credit_cost = get_utf8_bytes_size_from_file(file_path)
            current_credit_balance -= chapter_credit_cost

        if len(failed_files_dict["failed_files"]) > 0:
            failed_files_dict_list.append(failed_files_dict)
        
        print(f"All chapters exported successfully. Downloading audio files for project {folder_name}...")
        logging.info(f"All chapters exported successfully. Downloading audio files...")

        for download_link in download_links:
            download_from_link(download_link, folder_name, DOWNLOAD_FOLDER)
        
    display_failed_files(failed_files_dict_list)
