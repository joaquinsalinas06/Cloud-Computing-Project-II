import boto3
import uuid
import os

def lambda_handler(event, context):
    # Entrada (json)
    print(event)
    provider_id = event['body']['provider_id']
    user_id = event['body']['user_id']
    song_id = event['body']['song_id']
    text = event['body']['text']
    date = event['body']['date']
    nombre_tabla = os.environ["TABLE_NAME"]
    # Proceso
    comentario = {
        'provider_id': provider_id,
        'comment_id': user_id+"#"+date,
        'user_id': user_id,
        'song_id': song_id,
        'date': date,
        'text': text
    }
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)
    response = table.put_item(Item=comentario)
    # Salida (json)
    print(comentario)
    return {
        'statusCode': 200,
        'comentario': comentario,
        'response': response
    }
