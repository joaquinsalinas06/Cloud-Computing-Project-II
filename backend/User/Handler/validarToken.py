import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):

    token = event['headers']['Authorization']

    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Token not provided'})
        }
    
    dynamodb = boto3.resource('dynamodb')
    token_table_name = os.environ['TABLE2_NAME']  
    token_index_name = os.environ['INDEXGSI1_TABLE2_NAME']  
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.query(
        IndexName=token_index_name,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
    )
    
    if 'Items' not in response or not response['Items']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': "Token doesn't exist"})
        }

    token_data = response['Items'][0]
    expires = token_data.get('expiration')
    
    now = datetime.now()
    expiration_date = datetime.fromtimestamp(expires) if isinstance(expires, (int, float)) else datetime.strptime(expires, '%Y-%m-%d %H:%M:%S')
    
    if now > expiration_date:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token expired'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Token is valid'})
    }
