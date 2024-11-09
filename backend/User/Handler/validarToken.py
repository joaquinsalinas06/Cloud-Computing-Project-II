import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    # Retrieve token from the event
    token = event.get('token')

    if not token:
        return {
            'statusCode': 400,
            'body': {'error': 'Token not provided'}
        }
    
    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')
    token_table_name = 'dev-TokenTable'
    token_index_name = 'dev-TokenIndex'
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.query(
        IndexName=token_index_name,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
    )
    
    # Check if token exists in the response
    if 'Items' not in response or not response['Items']:
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    # Token expiration check
    token_data = response['Items'][0]
    expires = token_data.get('expires')
    now = datetime.now().timestamp()
    
    # Assume expires is a UNIX timestamp for simplicity
    if now > expires:
        return {
            'statusCode': 403,
            'body': {'error': 'Token expired'}
        }
    
    # Token is valid
    return {
        'statusCode': 200,
        'body': {'message': 'Token válido'}
    }
