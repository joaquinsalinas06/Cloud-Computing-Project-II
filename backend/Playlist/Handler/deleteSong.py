import boto3
import os
import json

def lambda_handler(event, context):
    try:
        playlist_id = event['pathParameters'].get('playlist_id')
        song_id = event['pathParameters'].get('song_id')

        if not playlist_id or not song_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing parameters'})
            }

        dynamodb = boto3.resource('dynamodb')
        playlist_table = dynamodb.Table(os.getenv('PLAYLIST_TABLE_NAME'))

        playlist_table.update_item(
            Key={'playlist_id': playlist_id},
            UpdateExpression="REMOVE songs.#song_id",
            ExpressionAttributeNames={'#song_id': song_id},
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Song removed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
