import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    token = event.get('token')

    if not token:
        return {
            'statusCode': 400,
            'body': {'error': 'Token not provided'}
        }
    
    dynamodb = boto3.resource('dynamodb')
    token_table_name = os.environ['TABLE2_NAME']
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.get_item(
        Key={'token': token}
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    expires = response['Item']['expires']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if now > expires:
        return {
            'statusCode': 403,
            'body': {'error': 'Token expired'}
        }
    
    return {
        'statusCode': 200,
        'body': {'message': 'Token válido'}
    }
