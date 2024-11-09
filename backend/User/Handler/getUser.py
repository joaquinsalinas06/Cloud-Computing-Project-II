import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event['path']['provider_id']
        user_id = event['path']['user_id']
        token = event['headers']['Authorization']
        
        if not provider_id or not user_id or not token:
            return {
                'statusCode': 400,
                'body': {'error': 'Missing parameters or token'}
            }

        payload = '{ "token": "' + token +  '" }'        
        lambda_client = boto3.client('lambda')
        invoke_response = lambda_client.invoke(
            FunctionName='api-mure-user-dev-validateToken',
            InvocationType='RequestResponse',
            Payload=payload
        )
        
        response_payload = json.loads(invoke_response['Payload'].read())
        
        if response_payload['statusCode'] != 200:
            return {
                'statusCode': 401,
                'body': {'error': 'Unauthorized',
                         'message': response_payload['body']['error']}
            }
        
        dynamodb = boto3.resource('dynamodb')
        user_table_name = os.environ['TABLE_NAME']
        user_table = dynamodb.Table(user_table_name)
        
        response = user_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': {'error': 'User not found'}
            }
        
        return {
            'statusCode': 200,
            'body': response['Items'][0]
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': f"Internal server error: {str(e)}"}
        }
