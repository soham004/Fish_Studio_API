import requests
import json
import sseclient
import logging

logging.basicConfig(filename="runtime.log",level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BEARER_TOKEN = None

base_headers = {
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

def retry(n):
    """
    A decorator that retries a function up to n times if it raises an exception.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, n + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed with error: {e}")
                    logging.error(f"Attempt {attempt} failed with error: {e}")
                    logging.info(f"Header: {base_headers}")
                    if attempt == n:
                        print("All retry attempts failed.")
                        raise
        return wrapper
    return decorator


def set_bearer_token(token):
    global BEARER_TOKEN
    global base_headers
    BEARER_TOKEN = token
    base_headers = {
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
    print(f"Bearer token set to: '{BEARER_TOKEN}'")
    logging.info(f"Bearer token set to: '{BEARER_TOKEN}'")

@retry(3)
def get_current_credit_balance(user_id:str)-> int:
    wallet_api_url = f"https://api.fish.audio/wallet/{user_id}/package"
    headers = base_headers.copy()
    response = requests.get(wallet_api_url, headers=headers)
    if response.status_code < 300:
        data = response.json()
        return data['balance']
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error fetching credit balance: {response.status_code}")

@retry(3)
def get_voice_id(voice_name:str)-> str:
    voice_api_url = f"https://api.fish.audio/model/latest-used?page_size=10&page_number=1"
    headers = base_headers.copy()
    response = requests.get(voice_api_url, headers=headers)
    if response.status_code < 300:
        voices = response.json()
        for voice in voices:
            # print(voice)
            if voice['title'] == voice_name:
                return voice['_id']
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error fetching voice ID: {response.status_code}")
    
@retry(3)
def create_studio_project(default_voice_id:str, default_backend:str, name:str)-> str:
    create_studio_project_api = "https://api.fish.audio/studio"
    headers = base_headers.copy()
    data = {
        "default_backend": default_backend,
        "default_voice_id": default_voice_id,
        "name": name,
    }
    response = requests.post(create_studio_project_api, headers=headers, json=data)
    if response.status_code < 300:
        data = response.json()
        return data['_id']
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error creating chapter: {response.status_code}")
        # return None

@retry(3)
def create_chapter(project_id:str, title:str)-> str:
    create_chapter_api = f"https://api.fish.audio/studio/{project_id}/chapters"
    headers = base_headers.copy()
    data = {
        "title": title
    }
    response = requests.post(create_chapter_api, headers=headers, json=data)
    if response.status_code < 300:
        data = response.json()
        return data['_id']
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error creating chapter: {response.status_code}")
        # return None

@retry(3)
def insert_text_block(content:str, studio_id:str, chapter_id:str, voice_id:str) -> str:
    insert_text_block_api = f"https://api.fish.audio/studio/{studio_id}/chapters/{chapter_id}/blocks"
    headers = base_headers.copy()
    data = {
        "content": content,
        "voice_id": voice_id,
    }
    response = requests.post(insert_text_block_api, headers=headers, json=data)
    if response.status_code < 300:
        # data = response.json()
        # return data['_id']
        pass
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error inserting text block: {response.status_code}")
        # return None

@retry(3)
def get_chapter_blocks(studio_id:str, chapter_id:str):
    get_chapter_blocks_api = f"https://api.fish.audio/studio/{studio_id}/chapters/{chapter_id}/blocks"
    headers = base_headers.copy()
    response = requests.get(get_chapter_blocks_api, headers=headers)
    if response.status_code < 300:
        data = response.json()
        return data
    elif response.status_code == 401:
        print(f"Error: Unauthorized. Please check your bearer token.")
        exit()
    else:
        raise Exception(f"Error fetching chapter blocks: {response.status_code}")

def export_chapter(studio_id:str, chapter_id:str):
    export_chapter_api = f"https://api.fish.audio/studio/{studio_id}/export"
    headers = base_headers.copy()
    headers['Accept'] = 'text/event-stream'
    data = {
        "audio_format":"mp3",
        "chapter_ids":[chapter_id],
        "export_subtitles": False,
        "pad_between_segments":0.2,
        "project_id":studio_id 
    }
    with requests.post(export_chapter_api, headers=headers, stream=True, json=data) as response:
        client = sseclient.SSEClient(response)
        i,f,j = 1,1,1
        for event in client.events():
            try:
                data = json.loads(event.data)
                event_type = data.get("type")
                # print("Received event:", data)
                if event_type == "generate-audio":
                    print(f"\rGenerating audio... {i}", end="\r")
                    i += 1
                if event_type == "generate-audio-finished":
                    print(f"\rFinished generating block: {f}", end="\r")
                    f += 1
                if event_type == "progress-fetch-audio":
                    print(f"\rFetching audio... {j}", end="\r")
                    j += 1
                if event_type == "message":
                    if data.get("message") == "concatenating-progress":
                        print(f"\rConcatenation progress: {data.get('progress')}%", end="\r")
                if event_type == "complete":
                    return data.get("url")
            except json.JSONDecodeError:
                print("Received non-JSON event:", event.data)
        
        print("\nExport process completed.")
