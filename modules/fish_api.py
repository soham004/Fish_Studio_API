import requests
import json
import sseclient
import logging

from modules.bearer_fetch import fetch_bearer_using_selenium

logging.basicConfig(filename="runtime.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry(n):
    """
    A decorator that retries a method up to n times if it raises an exception.
    """
    def decorator(func):
        def wrapper(self_obj, *args, **kwargs):
            for attempt in range(1, n + 1):
                try:
                    return func(self_obj, *args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed with error: {e} from function: {func.__name__}")
                    logging.error(f"Attempt {attempt} failed with error: {e} from function: {func.__name__}")
                    logging.info(f"Headers: {dict(self_obj.session.headers)}")
                    if attempt == n:
                        print("All retry attempts failed.")
                        raise
        return wrapper
    return decorator

class fish_api_calls:
    def __init__(self, token=None, session=None):
        self.BEARER_TOKEN = token
        
        # Use provided session or create new one
        self.session = session if session else requests.Session()
        
        # Set up session headers if token provided
        if token:
            self._configure_session_headers()
    
    def _configure_session_headers(self):
        """Configure the session headers with current token"""
        headers = {
            'Authorization': f'Bearer {self.BEARER_TOKEN}',
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
        self.session.headers.update(headers)

    def set_bearer_token(self, token):
        self.BEARER_TOKEN = token
        self._configure_session_headers()
        print(f"Bearer token set to: '{self.BEARER_TOKEN}'")
        logging.info(f"Bearer token set to: '{self.BEARER_TOKEN}'")

    def refresh_bearer_token(self):
        with open("config.json") as f:
            config = json.load(f)
        email = config['Email']
        password = config['Password']
        bearer_token = fetch_bearer_using_selenium(email, password)
        self.set_bearer_token(bearer_token)


    @retry(3)
    def get_current_credit_balance(self, user_id:str)-> int:
        wallet_api_url = f"https://api.fish.audio/wallet/{user_id}/package"
        response = self.session.get(wallet_api_url)
        if response.status_code < 300:
            data = response.json()
            return data['balance']
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error fetching credit balance: {response.status_code}")

    @retry(3)
    def get_voice_id(self, voice_name:str)-> str:
        voice_api_url = f"https://api.fish.audio/model/latest-used?page_size=10&page_number=1"
        response = self.session.get(voice_api_url)
        if response.status_code < 300:
            voices = response.json()
            for voice in voices:
                # print(voice)
                if voice['title'] == voice_name:
                    return voice['_id']
            return None
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error fetching voice ID: {response.status_code}")
        
    @retry(3)
    def create_studio_project(self, default_voice_id:str, default_backend:str, name:str)-> str:
        create_studio_project_api = "https://api.fish.audio/studio"
        data = {
            "default_backend": default_backend,
            "default_voice_id": default_voice_id,
            "name": name,
        }
        response = self.session.post(create_studio_project_api, json=data)
        if response.status_code < 300:
            data = response.json()
            return data['_id']
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error creating studio project: {response.status_code}")

    @retry(3)
    def create_chapter(self, project_id:str, title:str)-> str:
        create_chapter_api = f"https://api.fish.audio/studio/{project_id}/chapters"
        data = {
            "title": title[:20],
        }
        response = self.session.post(create_chapter_api, json=data)
        if response.status_code < 300:
            data = response.json()
            return data['_id']
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error creating chapter: {response.status_code}")

    @retry(3)
    def delete_chapter(self, studio_id:str, chapter_id:str)-> str:
        delete_chapter_api = f"https://api.fish.audio/studio/{studio_id}/chapters/{chapter_id}"

        response = self.session.options(delete_chapter_api) # This is just to simulate default browser baheviour

        response = self.session.delete(delete_chapter_api)
        if response.status_code < 300:
            return True
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error deleting chapter: {response.status_code}")

    @retry(3)
    def insert_text_block(self, content:str, studio_id:str, chapter_id:str, voice_id:str) -> str:
        insert_text_block_api = f"https://api.fish.audio/studio/{studio_id}/chapters/{chapter_id}/blocks"
        data = {
            "content": content,
            "voice_id": voice_id,
        }
        response = self.session.post(insert_text_block_api, json=data)
        if response.status_code < 300:
            # data = response.json()
            # return data['_id']
            pass
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error inserting text block: {response.status_code}")

    @retry(3)
    def get_chapter_blocks(self, studio_id:str, chapter_id:str):
        get_chapter_blocks_api = f"https://api.fish.audio/studio/{studio_id}/chapters/{chapter_id}/blocks"
        response = self.session.get(get_chapter_blocks_api)
        if response.status_code < 300:
            data = response.json()
            return data
        elif response.status_code == 401:
            print(f"Error: Unauthorized. Please check your bearer token.")
            exit()
        else:
            raise Exception(f"Error fetching chapter blocks: {response.status_code}")

    @retry(3)
    def export_chapter(self, studio_id:str, chapter_id:str):
        export_chapter_api = f"https://api.fish.audio/studio/{studio_id}/export"
        
        # Save the original Accept header value
        original_accept = self.session.headers.get('Accept', 'application/json')
        
        # Temporarily update the Accept header for SSE
        self.session.headers.update({'Accept': 'text/event-stream'})
        
        data = {
            "audio_format":"mp3",
            "chapter_ids":[chapter_id],
            "export_subtitles": False,
            "pad_between_segments":0.2,
            "project_id":studio_id 
        }
        
        try:
            with self.session.post(export_chapter_api, stream=True, json=data) as response:
                if response.status_code == 401:
                    print(f"Error: Unauthorized. Please check your bearer token.")
                    raise Exception("Unauthorized during export. Please check your bearer token.")
                client = sseclient.SSEClient(response)
                i, f, j = 1, 1, 1
                download_url = None
                for event in client.events():
                    try:
                        logging.info(f"Event: {event.data}")
                        data = json.loads(event.data)
                        event_type = data.get("type")
                        # print("Received event:", data)
                        if event_type == "generate-audio":
                            print(f"\rGenerating audio started... {i} ", end="\r")
                            i += 1
                        if event_type == "generate-audio-finished":
                            print(f"\rFinished generating block:  {f} ", end="\r")
                            f += 1
                        if event_type == "progress-fetch-audio":
                            print(f"\rFetching audio for block....{j} ", end="\r")
                            j += 1
                        if event_type == "message":
                            if data.get("message") == "concatenating-progress":
                                print(f"\rConcatenation progress: {data.get('progress')}%  ", end="\r")
                        if event_type == "complete":
                            download_url =  data.get("url")
                    except json.JSONDecodeError:
                        print("Received non-JSON event:", event.data)
                
                print("\nExport process completed.")
                logging.info("Export process completed.")
        finally:
            # Always restore the original Accept header
            self.session.headers.update({'Accept': original_accept})
        
        if download_url != None:
            return download_url
        else:
            raise Exception("Download URL not found in the export response.")
