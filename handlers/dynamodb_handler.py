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
        
    def get_ongoing_conversations(self):
        try:
            response = self.table.scan()
            ongoing_conversations = [item['OngoingConversationID'] for item in response['Items'] if 'OngoingConversationID' in item]
            return ongoing_conversations
        except Exception as e:
            raise RuntimeError(f"Error retrieving ongoing conversations from DynamoDB: {str(e)}")
        
    def update_ongoing_conversation(self, user_id, conversation_id):
        try:
            self.table.update_item(
                Key={'UserID': user_id},
                UpdateExpression="SET OngoingConversationID = :c",
                ExpressionAttributeValues={':c': conversation_id}
            )
        except Exception as e:
            raise RuntimeError(f"Error updating ongoing conversation in DynamoDB: {str(e)}")
        
    def remove_ongoing_conversation(self, user_id):
        try:
            self.table.update_item(
                Key={'UserID': user_id},
                UpdateExpression="REMOVE OngoingConversationID"
            )
        except Exception as e:
            raise RuntimeError(f"Error removing ongoing conversation from DynamoDB: {str(e)}")
