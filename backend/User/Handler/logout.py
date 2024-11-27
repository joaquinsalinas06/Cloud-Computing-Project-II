import boto3
import os
import json

def lambda_handler(event, context):
    provider_id = event['body']['provider_id']
    user_id = event['body']['user_id']

    token_table_name = os.environ['TABLE2_NAME']
    
    dynamodb = boto3.resource('dynamodb')
    token_table = dynamodb.Table(token_table_name)

    try:
        token_table.delete_item(
            Key={
                'provider_id': provider_id,
                'user_id': user_id
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Logout successful'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'status': 'error',
                'message': 'Could not logout'
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }
