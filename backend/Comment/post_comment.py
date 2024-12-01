import boto3
import uuid
import os
from boto3.dynamodb.conditions import Key
import json

def lambda_handler(event, context):
    # Entrada (json)
    print(event)

    token = event['headers']['Authorization']
    token_function = os.environ['LAMBDA_FUNCTION_NAME']        

    provider_id = event['path']['provider_id']
    
    lambda_client = boto3.client('lambda')
    payload = json.dumps({
            'token': token,
            'provider_id': provider_id
        })    
    
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



    user_id = event['path']['user_id']
    post_id = event['path']['post_id']
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
                'post_id': post_id,
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
