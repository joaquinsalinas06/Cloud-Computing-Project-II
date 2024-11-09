import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):

    token = event['token']

    if not token:
        return {
            'statusCode': 400,
            'body': {'error': 'Token not provided'}
        }
    
    dynamodb = boto3.resource('dynamodb')
    token_table_name = os.environ['TABLE2_NAME']  
    token_index_name = os.environ['INDEXGSI1_TABLE2_NAME']  
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.get_item(
        key={
            'token': token
        }
        )
    
    if 'Items' not in response:
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    else:
        expires = response['Item']['expires']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now > expires:
            return {
                'statusCode': 403,
                'body': 'Token expirado'
            }
    
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }
