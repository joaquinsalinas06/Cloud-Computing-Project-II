import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    # Retrieve token from the event
    token = event.get('token')
    print("Received token:", token)  # Debug: Check received token

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
    
    # Query using the Global Secondary Index on 'token'
    response = token_table.query(
        IndexName=token_index_name,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
    )
    
    print("DynamoDB Query Response:", response)  # Debug: Check if token is found

    # Check if token exists in the response
    if 'Items' not in response or not response['Items']:
        print("Token does not exist in the database")  # Debug: Token not found
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    # Token expiration check
    token_data = response['Items'][0]
    expires = token_data.get('expires')
    now = datetime.now().timestamp()
    print("Current time:", now)  # Debug: Check current time
    print("Token expiration time:", expires)  # Debug: Check expiration time

    # Assume expires is a UNIX timestamp
    if now > expires:
        print("Token has expired")  # Debug: Token expired
        return {
            'statusCode': 403,
            'body': {'error': 'Token expired'}
        }
    
    # Token is valid
    print("Token is valid")  # Debug: Token validation passed
    return {
        'statusCode': 200,
        'body': {'message': 'Token válido'}
    }
