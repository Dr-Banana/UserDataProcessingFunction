# handlers/dynamodb_handler.py

import boto3

class DynamoDBHandler:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def update_item(self, user_id, content):
        try:
            self.table.update_item(
                Key={'UserID': user_id},
                UpdateExpression="SET TodoList = :t",
                ExpressionAttributeValues={':t': content}
            )
        except Exception as e:
            raise RuntimeError(f"Error saving to DynamoDB: {str(e)}")
