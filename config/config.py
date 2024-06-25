# config/config.py

ENDPOINT_NAME = 'meta-llama'
TABLE_NAME = 'TodoList'
PRESET_PROMPT = "You are an assistant that summarizes text messages into structured JSON format. Output only the JSON document without any additional text. Example format: {\"event_1\": {\"brief\": \"xxx\", \"time\": \"xxx\", \"place\": \"xxx\", \"people\": \"xxx\", \"date\": \"xxx\"}}. If information is missing, ask for it."

PARAMETERS = {
    "max_new_tokens": 4096,
    "top_p": 0.9,
    "temperature": 0.6
}

OUTPUT_BUCKET_NAME = 'userdata-processing-output'