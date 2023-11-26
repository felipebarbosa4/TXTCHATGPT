import openai
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def query_chatgpt(question, api_key):
    openai.api_key = api_key

    try:
        # Assuming 'question' is a string with the user's input after the trigger phrase
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": question}]
        )
        # Return only the content of the assistant's response
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error querying ChatGPT: {e}")
        return ""

def process_text_file(file_path, api_key, last_processed):
    """
    Checks for the trigger phrase and updates the text file with the ChatGPT response.
    Continues monitoring until 'STOPTHISNOW' is encountered.
    """
    trigger_phrase = "ABCD1234"
    stop_phrase = "STOPTHISNOW"
    modified = False
    stop = False

    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(last_processed)  # Move to the last processed position
        content = file.read()  # Read the entire content of the file
        logging.info("Reading file content as a question.")

    # Check if the trigger phrase is in the entire file content
    if trigger_phrase in content:
        question = content.split(trigger_phrase)[-1].strip()
        print(question)
        logging.info(f"Trigger phrase found, sending query: {question}")
        response = query_chatgpt(question, api_key)
        if response:
            modified = True
            print(response)
            logging.info("Received response from ChatGPT, updating file.")
            # Replace the entire content of the file with the response
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("\n" "-------------------------------\n" + response + "\n")
        else:
            logging.warning("No response received, skipping update.")

    last_processed += len(content)
    return last_processed, stop

def watch_file(file_path, interval, api_key):
    """
    Watches the text file at the given path, performing the ChatGPT query
    when the trigger phrase is detected, and appending the response.
    Stops when 'STOPTHISNOW' is encountered.
    """
    last_processed = 0
    logging.info(f"Starting to watch file: {file_path}")
    while True:
        try:
            last_processed, stop = process_text_file(file_path, api_key, last_processed)
            if stop:
                logging.info("Stop phrase detected, stopping the watcher.")
                break
            time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Manual interruption received, stopping the watcher.")
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

def main():
    # Path to your text file
    file_path = 'mytextfile.txt'

    # How often to check the file for changes (in seconds)
    check_interval = 5

    # Your OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logging.error("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        return

    watch_file(file_path, check_interval, api_key)

if __name__ == "__main__":
    main()