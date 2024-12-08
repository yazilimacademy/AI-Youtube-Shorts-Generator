import openai
from dotenv import load_dotenv
import os
import json
import logging

# Configure logging
logging.basicConfig(
    filename='language_tasks_debug.log', 
    filemode='w', 
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Log environment variable presence
logging.debug("Checking environment variables...")
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logging.warning("OPENAI_API_KEY is not set in environment variables.")
else:
    logging.debug("OPENAI_API_KEY is set.")

# Set the API key for OpenAI and log it (partially)
openai.api_key = api_key
if openai.api_key:
    logging.debug("openai.api_key is set (not printing full key for security).")
else:
    logging.error("openai.api_key is not set! API calls will fail.")

def extract_times(json_string):
    logging.debug("Extracting times from JSON string.")
    try:
        data = json.loads(json_string)
        start_time = float(data[0]["start"])
        end_time = float(data[0]["end"])
        start_time_int = int(start_time)
        end_time_int = int(end_time)
        logging.debug(f"Extracted start_time: {start_time_int}, end_time: {end_time_int}")
        return start_time_int, end_time_int
    except Exception as e:
        logging.exception("Failed to extract times:", exc_info=e)
        return 0,0

# Updated system prompt to strictly require JSON only
system = '''
You are a helpful assistant. The user provides a transcription of a video. 
Your task: Extract a single continuous highlight (less than 1 minute) from the transcription that could be a great short highlight.

Return exactly and only one JSON array with this format (no extra text, no code fences):

[
  {
    "start": <start time in seconds, an integer>,
    "content": "<highlight text>",
    "end": <end time in seconds, an integer>
  }
]

If no valid highlight is found, return:
[{"start":0,"end":0,"content":""}]
Do not include any explanation or additional text outside this JSON.
'''

def GetHighlight(Transcription):
    print("Getting Highlight from Transcription")
    logging.debug("Entered GetHighlight function.")
    logging.debug(f"Transcription length: {len(Transcription)}")
    logging.debug(f"Transcription snippet: {Transcription[:200]}...")

    # Use a stable known model if possible
    model_name = "gpt-4o"  
    temperature_value = 0.7
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": Transcription}
    ]

    logging.debug(f"Preparing OpenAI call with model: {model_name}")
    logging.debug(f"Temperature: {temperature_value}")
    logging.debug(f"Messages: {messages}")

    try:
        # DO NOT CHANGE THE LINE BELOW BECAUSE IT IS THE NEW VERSION OF IT.
        response = openai.chat.completions.create(
            model=model_name,
            temperature=temperature_value,
            messages=messages,
        )
        # END OF THE LINE THAT SHOULD NOT BE CHANGED
        print(f"response object:{response}")

        logging.debug("OpenAI response received successfully.")
        json_string = response.choices[0].message.content
        print(json_string)
        logging.info(f"Response from OpenAI: {json_string}")

        Start, End = extract_times(json_string)
        if Start == End:
            logging.warning("Start and End times are equal. Possibly no valid highlight found.")
            Ask = input("Error - Get Highlights again (y/n) -> ").lower()
            if Ask == 'y':
                logging.debug("User chose to retry getting highlight.")
                Start, End = GetHighlight(Transcription)
        return Start, End

    except Exception as e:
        logging.exception("Exception occurred while creating OpenAI completion:", exc_info=e)
        print("Error occurred during highlight generation. Check language_tasks_debug.log for details.")
        return 0, 0

if __name__ == "__main__":
    User = "Any Example"
    result = GetHighlight(User)
    logging.debug(f"Final result from GetHighlight: {result}")
    print(result)
