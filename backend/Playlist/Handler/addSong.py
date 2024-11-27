import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event['pathParameters'].get('provider_id')
        playlist_id = event['pathParameters'].get('playlist_id')
        song_id = event['pathParameters'].get('song_id')
        token = event['headers']['Authorization']        
        song_details = json.loads(event['body']).get('song_details')

        if not provider_id or not playlist_id or not song_id or not song_details or not token:
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
        playlist_table = dynamodb.Table(os.getenv('PLAYLIST_TABLE_NAME'))

        playlist_table.update_item(
            Key={'provider_id': provider_id, 'playlist_id': playlist_id},
            UpdateExpression="SET songs.#song_id = :song_details",
            ExpressionAttributeNames={'#song_id': song_id},
            ExpressionAttributeValues={':song_details': song_details},
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Song added to playlist successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }