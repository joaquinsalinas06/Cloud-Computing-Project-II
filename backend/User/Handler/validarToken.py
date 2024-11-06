import boto3 
from datetime import datetime
import os

def lambda_handler(event, context):
    token = event.get('token')
    dynamodb = boto3.resource('dynamodb')
    token_table_name = os.getenv('TABLE2_NAME_e')
    token_table = dynamodb.Table(token_table_name)
    response = token_table.get_item(
        Key={
            'token': token
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Token doesn\'t exist'
        }
    else:
        expires = response['Item']['expiration']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now > expires:
            return {
                'statusCode': 403,
                'body': 'Token expired'
            }
    return {
        'statusCode': 200,
        'body': 'Token is valid'
    }