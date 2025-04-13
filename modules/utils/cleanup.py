import re
import html

def textCleanUp(text:str) -> str:

    text = text.encode('utf-8', 'ignore').decode('utf-8')  # Remove invalid utf-8 chars
    text = text.replace("\n", " ").strip().replace("  ", " ")
    text = re.sub(r'[\x00-\x1F\x7F\xa0]', ' ', text)
    
    text = html.unescape(text)

    # Remove zero-width characters
    text = re.sub(r'[\u200B\u200C\u200D\u2060\uFEFF]', '', text)

    # Replace non-breaking space with a normal space
    text = text.replace("\xa0", " ")

    # Remove control characters and non-printable characters
    text = re.sub(r'[\x00-\x1F\x7F\u202A-\u202E]', '', text)

    # Normalize newlines (optional: replace with space or keep)
    text = re.sub(r'[\r\n]+', ' ', text)

    # Remove excessive spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text