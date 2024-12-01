import boto3
from datetime import datetime
import os
import json

def lambda_handler(event, context):
    token = event.get('token')
    provider_id = event.get('provider_id')

    print("Received token:", token)  
    print("Received provider_id:", provider_id)

    if not token or not provider_id:
        return {
            'statusCode': 400,
            'body': {'error': 'Token or provider_id not provided'}
        }
    
    dynamodb = boto3.resource('dynamodb')
    token_table_name = os.environ['TABLE2_NAME']
    token_index_name = os.environ['LSI2'] 
    print("Token table name:", token_table_name)
    print("Token index name:", token_index_name)
    token_table = dynamodb.Table(token_table_name)
    
    try:
        response = token_table.query(
            IndexName=token_index_name,  
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('token').eq(token)  
        )
        
        print("DynamoDB Query Response:", response) 

        if 'Items' not in response or not response['Items']:
            print("Token does not exist in the database")  
            return {
                'statusCode': 403,
                'body': {'error': "Token doesn't exist"}
            }

        token_data = response['Items'][0] 
        expires = token_data['expiration']
        now = datetime.now().timestamp()
        
        print("Current time:", now) 
        print("Token expiration time:", expires)  
        
        expiration_timestamp = datetime.strptime(expires, '%Y-%m-%d %H:%M:%S').timestamp()
        if now > expiration_timestamp:
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

    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': f"Internal server error: {str(e)}"}
        }
