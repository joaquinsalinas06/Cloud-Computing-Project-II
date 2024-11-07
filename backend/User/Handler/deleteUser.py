import boto3
import os
import json

def lambda_handler(event, context):
    try:
        user_id = event['pathParameters'].get('user_id')
        provider_id = event['pathParameters'].get('provider_id')
        token = event['headers'].get('Authorization')
        
        if not provider_id or not user_id or not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing parameters or token'})
            }
        
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
        
        if invoke_response['StatusCode'] != 200 or response_payload.get('statusCode') != 200:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        dynamodb = boto3.resource('dynamodb')
        user_table_name = os.getenv('TABLE_NAME_e')
        token_table_name = os.getenv('TABLE2_NAME_e')
        user_table = dynamodb.Table(user_table_name)
        token_table = dynamodb.Table(token_table_name)
        
        response = user_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }
        
        user_table.delete_item(
            Key={
                'provider_id': provider_id,
                'user_id': user_id
            }
        )
        
        token_response = token_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        if 'Items' in token_response:
            for item in token_response['Items']:
                token_table.delete_item(
                    Key={
                        'provider_id': provider_id,
                        'user_id': user_id,
                        'token': item['token']
                    }
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User and associated tokens deleted'})
        }
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
