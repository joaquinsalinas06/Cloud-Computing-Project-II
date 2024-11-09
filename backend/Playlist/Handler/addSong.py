import boto3
import os
import json

def lambda_handler(event, context):
    try:
        playlist_id = event['pathParameters'].get('playlist_id')
        song_id = event['pathParameters'].get('song_id')
        song_details = json.loads(event['body']).get('song_details')

        if not playlist_id or not song_id or not song_details:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing parameters'})
            }

        dynamodb = boto3.resource('dynamodb')
        playlist_table = dynamodb.Table(os.getenv('PLAYLIST_TABLE_NAME'))

        playlist_table.update_item(
            Key={'playlist_id': playlist_id},
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
