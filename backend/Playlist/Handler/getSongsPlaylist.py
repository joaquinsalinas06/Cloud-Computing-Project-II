import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event['path']['provider_id']
        playlist_id = event['path']['playlist_id']
        token = event['headers']['Authorization']

        if not playlist_id or not provider_id or not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing playlist_id or provider_id or token parameter'})
            }

        payload = json.dumps({
            'token': token,
            'provider_id': provider_id
        })  
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

        response = playlist_table.get_item(Key={'provider_id':provider_id, 'playlist_id': playlist_id})
        playlist = response.get('Item')

        if not playlist:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Playlist not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'songs': playlist.get('songs', [])})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
