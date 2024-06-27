# config/config.py

ENDPOINT_NAME = 'meta-llama'
PRESET_PROMPT = "You are an assistant that summarizes text messages into a structured JSON format. Output only the JSON document without any additional text. Example format: {\"event_1\": {\"brief\": \"xxx\", \"time\": \"xxx\", \"place\": \"xxx\", \"people\": \"xxx\", \"date\": \"xxx\"}, ...}. If any of these fields are not mentioned, use null as the value. 'brief' refers to a short description of the event, 'time' refers to the time of the event, 'place' refers to the location of the event, 'people' refers to the individuals involved in the event (including 'me' or 'I' as one of the participants if applicable), and 'date' refers to the date of the event. If any required information is missing, do not use placeholders like 'xxx'; instead, use null."

PARAMETERS = {
    "max_new_tokens": 4096,
    "top_p": 0.9,
    "temperature": 0.6
}

OUTPUT_BUCKET_NAME = "userdata-processing-output"
TABLE_NAME = 'TodoList'