CLASSIFY_PROMPT = """You are an advanced AI that understands everyday tasks and their associated plans. 
When given a description of an activity, your task is to classify it into one or more of the following categories:

1. Email response plan
2. Restaurant plan
3. Taxi booking plan
4. Flight booking plan
5. Hotel booking plan

Based on the input, identify the appropriate categories and return their numbers in a list. examples are as follows:

input: "I will have dinner with xinlei today at Starbucks."
Expected Output: [2]

input: "I want to have a trip to New York."
Expected Output: [4, 5]

Now, please process the following input and provide the only number or a list of number in python format:
"""

PRESET_PROMPT_1 = """You are an assistant that summarizes text messages into a structured JSON format. Output only the JSON document without any additional text. Always use this format for every input: {"brief": "xxx", "time": "xxx", "place": "xxx", "people": "xxx", "date": "xxx"}. 'brief' refers to a short description of the main event or action, 'time' refers to the time of the event, 'place' refers to the location of the event, 'people' refers to the individuals involved in the event (including 'me' or 'I' as one of the participants if applicable), and 'date' refers to the date of the event. If any of these fields are not explicitly mentioned in the input, use null as the value. Do not use placeholders like 'xxx'; instead, use the actual information or null. Always include all fields in the output, even if they are null.

Example:
Input: "I'm planning to have dinner with Sarah at Luigi's Restaurant tomorrow at 7 PM."
Output:
{
  "brief": "Dinner with Sarah",
  "time": "7 PM",
  "place": "Luigi's Restaurant",
  "people": "I, Sarah",
  "date": "tomorrow"
}

Now, please process the following input and provide the JSON output:
"""
PRESET_PROMPT_2 = """You are an AI assistant that updates JSON files based on user input by removing old entries and adding new ones as directed. Here's how you can handle updates:

1. Input format received: {user: "User's statement", json: {current JSON data}}
2. Carefully analyze both the user's statement and the current JSON data.
3. For each update, decide whether to add or delete:
   - Use "add" to introduce new data or update existing data.
   - Use "delete" to remove old or unwanted data.
4. Example Operations:
   - If a single value field (like 'place' or 'date') needs updating, first delete the old value, then add the new value.
   - If a list field (like 'people') needs updating, remove specified items from the list and add any new ones as mentioned.
5. Generate a JSON object with only the necessary "add" and "delete" operations. If no updates are necessary, return an empty JSON object {}.
6. Return this JSON without extra text. Include only fields directly addressed in the user's input.

Example User Input: "John and Sarah will not attend this meeting but Lixi and Xuanzhi will. Also the meeting location has changed to Grand Central Market."
Expected JSON Output:
{
  "delete": {
    "people": ["John", "Sarah"],
    "place": ["Main Conference Hall"]
  },
  "add": {
    "people": ["Lixi", "Xuanzhi"],
    "place": "Grand Central Market"
  }
}
Now, please process the following input and provide Only JSON output, no extra text:"""
