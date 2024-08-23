# config/templates.py
from config import PARAMETERS

def llama_template(preset_prompt, input_text):
    return {
        "inputs": [
            [
                {"role": "system", "content": preset_prompt},
                {"role": "user", "content": input_text}
            ]
        ],
        "parameters": PARAMETERS
    }
