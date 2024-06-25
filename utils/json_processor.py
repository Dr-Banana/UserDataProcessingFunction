import json

def process_incomplete_response(response, user_id):
    # 从SageMaker响应中提取提问信息
    question = response['question']
    
    # 返回一个需要用户回答的JSON
    return {
        'needs_confirmation': True,
        'user_id': user_id,
        'question': question
    }
