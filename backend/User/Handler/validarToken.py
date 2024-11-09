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
    token_table_name = 'dev-tokens-table'
    token_index_name = os.environ['INDEXLSI1_TABLE2_NAME']
    print("Token table name:", token_table_name)
    print("Token index name:", token_index_name)
    token_table = dynamodb.Table(token_table_name)
    
    response = token_table.query(
        IndexName=token_index_name,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
    )
    
    print("DynamoDB Query Response:", response) 

    if 'Item' not in response:
        print("Token does not exist in the database")  
        return {
            'statusCode': 403,
            'body': {'error': "Token doesn't exist"}
        }

    token_data = response['Item']
    expires = response['Item']['expiration']  
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
