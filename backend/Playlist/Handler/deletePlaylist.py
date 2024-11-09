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

        playlist_table.delete_item(Key={'playlist_id': playlist_id})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Playlist deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
