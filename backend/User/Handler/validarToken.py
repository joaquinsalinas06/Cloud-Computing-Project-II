import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    token = event['token']
    print("Received token:", token)  

    if not token:
        return {
            'statusCode': 400,
            'body': {'error': 'Token not provided'}
        }
    
    dynamodb = boto3.resource('dynamodb')
    token_table_name = 'dev-TokenTable'
    token_index_name = 'dev-TokenIndex'
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.query(
        IndexName=token_index_name,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
    )
    
    print("DynamoDB Query Response:", response) 
    if 'Items' not in response or not response['Items']:
        print("Token does not exist in the database")  
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    token_data = response['Items'][0]
    expires = token_data.get('expires')
    now = datetime.now().timestamp()
    print("Current time:", now) 
    print("Token expiration time:", expires)  
    if now > expires:
        print("Token has expired")  
        return {
            'statusCode': 403,
            'body': {'error': 'Token expired'}
        }
    
    print("Token is valid")  
    return {
        'statusCode': 200,
        'body': {'message': 'Token válido'}
    }
