import boto3
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    try:
        provider_id = event['pathParameters']['provider_id']
        user_id = event['pathParameters']['user_id']
        token = event['headers']['Authorization']
        
        # Invocar la función Lambda de autorización
        lambda_client = boto3.client('lambda')
        payload = {
            "provider_id": provider_id,
            "user_id": user_id,
            "token": token
        }
        
        invoke_response = lambda_client.invoke(
            FunctionName=os.getenv('AUTHORIZER_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.load(invoke_response['Payload'])
        print(response_payload)
        
        if invoke_response['StatusCode'] != 200 or response_payload.get('authorized') != True:
            return {
                'statusCode': 401,
                'body': 'Unauthorized'
            }
        
        # Consultar DynamoDB para obtener los datos del usuario
        dynamodb = boto3.resource('dynamodb')
        user_table_name = os.getenv('TABLE_NAME_e')
        user_table = dynamodb.Table(user_table_name)
        
        response = user_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': 'User not found'
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'][0])
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Internal server error: {str(e)}"
        }