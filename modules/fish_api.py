import requests
import json

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

def get_current_credit_balance(user_id:str)-> int:
    wallet_api_url = f"https://api.fish.audio/wallet/{user_id}/package"
    headers = base_headers.copy()
    response = requests.get(wallet_api_url, headers=headers)
    if response.status_code < 300:
        data = response.json()
        return data['balance']
    else:
        print(f"Error fetching credit balance: {response.status_code}")
        return None

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
    else:
        print(f"Error fetching voice ID: {response.status_code}")
        return None
    
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
    else:
        print(f"Error creating chapter: {response.status_code}")
        return None

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
    else:
        print(f"Error creating chapter: {response.status_code}")
        return None