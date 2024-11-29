import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event['path']['provider_id']
        user_id = event['path']['user_id']
        user_id = int(user_id)
        token = event['headers']['Authorization']
        
        if not provider_id or not user_id or not token:
            return {
                'statusCode': 400,
                'body': {'error': 'Missing parameters or token'}
            }

        payload = '{ "token": "' + token +  '" }'        
        lambda_client = boto3.client('lambda')
        token_function = os.environ['AUTHORIZER_FUNCTION_NAME']
        invoke_response = lambda_client.invoke(
            FunctionName=token_function,
            InvocationType='RequestResponse',
            Payload=payload
        )
        
        response_payload = json.loads(invoke_response['Payload'].read())
        print("Response Payload:", response_payload) 
        
        if 'statusCode' not in response_payload or response_payload['statusCode'] != 200:
            error_message = response_payload.get('body', {}).get('error', 'Unknown error')
            return {
                'statusCode': 401,
                'body': {'error': 'Unauthorized', 'message': error_message}
            }
             
        dynamodb = boto3.resource('dynamodb')
        user_table_name = os.getenv('TABLE_NAME')
        token_table_name = os.getenv('TABLE2_NAME')
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

        token_index_name = os.environ['LSI2']
        
        token_response = token_table.query(
            IndexName=token_index_name,
            KeyConditionExpression=boto3.dynamodb.conditions.Key('token').eq(token)
        )
        
        if 'Items' in token_response:
            for item in token_response['Items']:
                token_table.delete_item(
                    Key={
                        'provider_id': item['provider_id'],  
                        'email': item['email']  
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
