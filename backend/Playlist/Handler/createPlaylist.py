import boto3
import os
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:      
        provider_id = event['body']['provider_id']
        user_id = event['body']['user_id']
        name = event['body']['name']
        token = event['headers']['Authorization']
    
        if not provider_id or not user_id or not name or not token:
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
        table_name = os.environ['TABLE_NAME']
        playlist_table = dynamodb.Table(table_name)

        response = playlist_table.query(
            KeyConditionExpression=Key('provider_id').eq(provider_id),
            ScanIndexForward=False, 
            Limit=1
        )

        highest_playlist_id = 0
        if 'Items' in response and response['Items']:
            highest_playlist_id = int(response['Items'][0]['playlist_id'])

        new_playlist_id = highest_playlist_id + 1
        
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        playlist_table.put_item(
            Item={
                'provider_id': provider_id,
                'playlist_id': str(new_playlist_id),
                'user_id': user_id,
                'playlist_name': playlist_name,
                'date_created': date_created,
                'songs': []
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Playlist created successfully',
                'playlist_id': new_playlist_id
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
