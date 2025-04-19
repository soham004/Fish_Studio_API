import time
from modules.utils.cleanup import textCleanUp

def split_text_by_period(filename: str, limit: int) -> list:
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read().strip()  # Strip any extra whitespace at the start and end
        text = textCleanUp(text)  # Clean up the text
    
    chunks = []
    start = 0

    while start < len(text):
        end = start + limit

        if end >= len(text):  # End of text reached
            chunk = text[start:].strip()
            if chunk:  # Ensure no empty chunk is added
                chunks.append(chunk)
            break

        # Look for the nearest period (.) or question mark (?) after the limit
        stop_pos = text.find('.', end)
        qmark_pos = text.find('?', end)

        # Find the nearest valid stopping position
        if stop_pos == -1:
            stop_pos = float('inf')
        if qmark_pos == -1:
            qmark_pos = float('inf')

        best_pos = min(stop_pos, qmark_pos)

        # If a stopping point is found within a reasonable range, extend the chunk
        if best_pos != float('inf') and best_pos - start < limit * 1.5:
            end = best_pos + 1  # Include the period or question mark

        chunk = text[start:end].strip()
        if chunk:  # Ensure no empty chunk is added
            chunks.append(chunk)

        start = end  # Move to the next part

    return chunks


def get_utf8_bytes_size_from_file(filename: str) -> int:
    with open(filename, 'rb') as file:
        content = file.read()
    return len(content)

def get_utf8_bytes_size_from_files(filenames: list) -> int:
    # Use textCleanUp to clean up the text before calculating size
    total_size = 0
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
            cleaned_text = textCleanUp(text)
            total_size += len(cleaned_text.encode('utf-8'))
    return total_size

if __name__ == "__main__":
    while True:
        file = input("Please input the file to splice.\n>>>")
        if not file.endswith(".txt"):
            print(f"Invalid file: {file}\nTry again.")
            continue
        try:
            charLen = int(input("Please input the character limit per chunk.\n>>>"))
        except ValueError:
            print("Invalid input. Please input an integer.")
            continue
        try:
            chunks = split_text_by_period(file, charLen)
            it = 1
            for chunk in chunks:
                output = f"output/chunk{it}.txt"
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                print(f"Chunk {it} saved to {output}")

                it += 1

            print(f"\nSuccess. You can close by pressing the exit button or CTRL + C twice.")
            time.sleep(5)
        except Exception as e:
            print(f"An error occured: {e}. Restarting...")
            time.sleep(3)
