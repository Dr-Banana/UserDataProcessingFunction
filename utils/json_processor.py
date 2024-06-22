# utils/json_processor.py

import json

def process_json(llama_output):
    try:
        content = llama_output[0]['generation']['content']
        
        # 过滤出JSON部分
        json_start = content.index('{')
        json_content = content[json_start:]
        
        # 解析JSON
        parsed_json = json.loads(json_content)
        return parsed_json
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        raise RuntimeError(f"Error processing JSON: {str(e)}")
