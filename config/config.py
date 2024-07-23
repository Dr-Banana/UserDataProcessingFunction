# config/config.py

ENDPOINT_NAME = 'meta-llama'
PRESET_PROMPT = "You are an assistant that summarizes text messages into a structured JSON format. Output only the JSON document without any additional text. Always use this format for every input: {\"event_1\": {\"brief\": \"xxx\", \"time\": \"xxx\", \"place\": \"xxx\", \"people\": \"xxx\", \"date\": \"xxx\"}}. 'brief' refers to a short description of the main event or action, 'time' refers to the time of the event, 'place' refers to the location of the event, 'people' refers to the individuals involved in the event (including 'me' or 'I' as one of the participants if applicable), and 'date' refers to the date of the event. If any of these fields are not explicitly mentioned in the input, use null as the value. Do not use placeholders like 'xxx'; instead, use the actual information or null. Always include all fields in the output, even if they are null."
PARAMETERS = {
    "max_new_tokens": 4096,
    "top_p": 0.9,
    "temperature": 0.6
}

OUTPUT_BUCKET_NAME = "userdata-processing-output"
TODO_TABLE_NAME = 'TodoList'
CONVERSATION_TABLE_NAME = 'Conversation'