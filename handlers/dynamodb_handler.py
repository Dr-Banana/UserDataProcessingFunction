# handlers/dynamodb_handler.py
from config.config import TODO_TABLE_NAME, CONVERSATION_TABLE_NAME
import boto3

class DynamoDBHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

        self.todo_table_name = TODO_TABLE_NAME
        self.todo_table = self.dynamodb.Table(TODO_TABLE_NAME)

        self.conver_table_name = CONVERSATION_TABLE_NAME
        self.conver_table = self.dynamodb.Table(CONVERSATION_TABLE_NAME)

    def update_item(self, user_id, content):
        try:
            self.todo_table.update_item(
                Key={'UserID': user_id},
                UpdateExpression="SET TodoList = :t",
                ExpressionAttributeValues={':t': content}
            )
        except Exception as e:
            raise RuntimeError(f"Error saving to DynamoDB: {str(e)}")

    def save_save_eventID(self, conversation_id, user_id):
        try:
            self.conver_table.put_item(
                Item={
                    'EventID': conversation_id,
                    'UserID': user_id
                }
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Error saving conversation to DynamoDB: {str(e)}")