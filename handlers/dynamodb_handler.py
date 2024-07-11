# handlers/dynamodb_handler.py
from config.config import TODO_TABLE_NAME, CONVERSATION_TABLE_NAME
import boto3

class DynamoDBHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

        self.conver_table_name = CONVERSATION_TABLE_NAME
        self.conver_table = self.dynamodb.Table(CONVERSATION_TABLE_NAME)

    def update_item(self, user_id, eventID, content):
        try:
            self.conver_table.put_item(
                Item={
                    'UserID': user_id,
                    'ConversationID': eventID,
                    'Content': content
                }
            )
            self.conver_table.update_item(
                Key={
                    'UserID': user_id,
                    'ConversationID': eventID
                },
                UpdateExpression="SET Content = :c",
                ExpressionAttributeValues={':c': content}
            )
        except Exception as e:
            raise RuntimeError(f"Error saving to DynamoDB: {str(e)}")