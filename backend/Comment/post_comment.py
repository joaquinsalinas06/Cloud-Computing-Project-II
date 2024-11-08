import boto3
import uuid
import os
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Entrada (json)
    print(event)
    provider_id = event['body']['provider_id']
    user_id = event['body']['user_id']
    song_id = event['body']['song_id']
    text = event['body']['text']
    date = event['body']['date']
    nombre_tabla = os.environ["TABLE_NAME"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)

    response = table.query(
        KeyConditionExpression=Key('provider_id').eq(provider_id),
        ScanIndexForward=False,
        Limit=1
    )

    highestSortKey = 0
    if response['Count'] > 0:
        highestSortKey = int(response['Items'][0]['comment_id'])
    saved = False
    while not saved:
        try:
            # Increment the comment_id if it’s in sequence
            comentario = {
                'provider_id': provider_id,
                'comment_id': highestSortKey + 1,
                'user_id': user_id,
                'song_id': song_id,
                'date': date,
                'text': text
            }
            response = table.put_item(
                Item=comentario,
                ConditionExpression='attribute_not_exists(provider_id)'
            )
            saved = True
        except table.meta.client.exceptions.ConditionalCheckFailedException:
            highestSortKey += 1

    # Salida (json)
    print(comentario)
    return {
        'statusCode': 200,
        'comentario': comentario,
        'response': response
    }
