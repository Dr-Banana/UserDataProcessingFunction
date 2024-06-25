import boto3
import json
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def save_to_dynamodb(user_id, result):
    table = dynamodb.Table('TodoList')  # 确认表名是否正确
    response = table.update_item(
        Key={'UserID': user_id},
        UpdateExpression="SET TodoList = :t",
        ExpressionAttributeValues={':t': result}
    )
    return response
