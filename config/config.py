# config/config.py

ENDPOINT_NAME = 'meta-llama'
PRESET_PROMPT = "You are an assistant that summarizes text messages into a structured JSON format. Output only the JSON document without any additional text. First, determine if the input is generating a to-do list or if it's a discussion with the AI. If it's a to-do list, use this format: {\"event_1\": {\"brief\": \"xxx\", \"time\": \"xxx\", \"place\": \"xxx\", \"people\": \"xxx\", \"date\": \"xxx\"}, ...}. If any of these fields are not mentioned, use null as the value. 'brief' refers to a short description of the event, 'time' refers to the time of the event, 'place' refers to the location of the event, 'people' refers to the individuals involved in the event (including 'me' or 'I' as one of the participants if applicable), and 'date' refers to the date of the event. If any required information is missing, do not use placeholders like 'xxx'; instead, use null. If the input appears to be a discussion with the AI, use this format instead: {\"event_1\": \"discuss\"}."

PARAMETERS = {
    "max_new_tokens": 4096,
    "top_p": 0.9,
    "temperature": 0.6
}

OUTPUT_BUCKET_NAME = "userdata-processing-output"
TODO_TABLE_NAME = 'TodoList'
CONVERSATION_TABLE_NAME = 'Conversation'