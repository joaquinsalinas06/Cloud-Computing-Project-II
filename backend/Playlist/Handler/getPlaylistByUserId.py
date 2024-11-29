import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event["path"]["provider_"]
        user_id = event['path']['user_id']
        token = event['headers']['Authorization']

        if not user_id or not provider_id or not token:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing user_id parameter or Authorization header'})
            }

        payload = json.dumps({ "token": token })
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
                'body': json.dumps({'error': 'Unauthorized', 'message': error_message})
            }
            
        dynamodb = boto3.resource('dynamodb')
        playlist_table = dynamodb.Table(os.getenv('TABLE_NAME'))

        user_index = os.environ['LSI']
        
        response = playlist_table.query(
            IndexName=user_index,
            KeyConditionExpression='provider_id = :provider_id and user_id = :user_id',
            ExpressionAttributeValues={ ':provider_id': provider_id, ':user_id': user_id}
        )

        playlists = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps({'playlists': playlists})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
