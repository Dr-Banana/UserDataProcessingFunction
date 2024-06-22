# config/templates.py
def get_input_data_json(preset_prompt, input_text, parameters):
    return {
        "inputs": [
            [
                {"role": "system", "content": preset_prompt},
                {"role": "user", "content": input_text}
            ]
        ],
        "parameters": parameters
    }
