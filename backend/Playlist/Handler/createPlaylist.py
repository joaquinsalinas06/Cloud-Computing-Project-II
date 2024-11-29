import boto3
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    try:
        provider_id = event['path']['provider_id']
        playlist_id = event['path']['playlist_id']
        user_id = event['path']['user_id']
        body = json.loads(event['body'])
        playlist_name = body['playlist_name']
        token = event['headers']['Authorization']        

        if not provider_id or not playlist_id or not user_id or not playlist_name or not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing parameters'})
            }

        payload = '{ "token": "' + token +  '" }'        
        lambda_client = boto3.client('lambda')
        token_function = os.environ['LAMBDA_FUNCTION_NAME']

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
        playlist_table = dynamodb.Table(os.getenv('TABLE_NAME'))

        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        playlist_table.put_item(
            Item={
                'provider_id': provider_id,
                'playlist_id': playlist_id,
                'user_id': user_id,
                'playlist_name': playlist_name,
                'date_created': date_created,
                'songs': []
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Playlist created successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }