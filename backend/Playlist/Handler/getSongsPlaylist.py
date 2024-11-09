import boto3
import os
import json

def lambda_handler(event, context):
    try:
        playlist_id = event['pathParameters'].get('playlist_id')

        if not playlist_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing playlist_id parameter'})
            }

        dynamodb = boto3.resource('dynamodb')
        playlist_table = dynamodb.Table(os.getenv('PLAYLIST_TABLE_NAME'))

        response = playlist_table.get_item(Key={'playlist_id': playlist_id})
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
