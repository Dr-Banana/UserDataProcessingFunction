import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
from config import TABLE_NAME

def save_to_dynamodb(user_id, result):
    table = dynamodb.Table(TABLE_NAME)
    response = table.update_item(
        Key={'UserID': user_id},
        UpdateExpression="SET TodoList = :t",
        ExpressionAttributeValues={':t': result}
    )
    return response
