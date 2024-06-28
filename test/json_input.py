import json

ENDPOINT_CONNECT_TEST = {"body": "{\r\n    \"action\": \"test\"\r\n}\r\n"}
LLAMA_RESPONSE_TEST = [
            {
                "generation": {
                    "content": json.dumps({
                        "event_1": {
                            "brief": "Meeting with team",
                            "time": "10:00 AM",
                            "place": "Conference Room",
                            "people": "Team members",
                            "date": "2024-06-28"
                        }
                    })
                }
            }
        ]