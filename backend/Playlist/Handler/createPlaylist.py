import boto3
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    try:
        provider_id = event['pathParameters'].get('provider_id')
        playlist_id = event['pathParameters'].get('playlist_id')
        user_id = event['pathParameters'].get('user_id')
        body = json.loads(event['body'])
        playlist_name = body.get('playlist_name')

        if not provider_id or not playlist_id or not user_id or not playlist_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing parameters'})
            }

        dynamodb = boto3.resource('dynamodb')
        playlist_table = dynamodb.Table(os.getenv('PLAYLIST_TABLE_NAME'))

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