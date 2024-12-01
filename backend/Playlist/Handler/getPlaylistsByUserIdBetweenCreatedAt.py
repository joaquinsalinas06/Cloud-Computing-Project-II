import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    gsi_name = os.environ['GSI']

    user_id = event['path']['user_id']
    provider_id = event['body']['provider_id']
    start_created_at = event['query']['start_created_at']
    end_created_at = event['query']['end_created_at']
    token = event['headers']['Authorization']


    if not user_id or not start_created_at or not end_created_at:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: user_id, start_created_at, end_created_at'})
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

    try:
        start_date = datetime.strptime(start_created_at, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_created_at, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid date format. Expected YYYY-MM-DD HH:MM:SS'})
        }

    try:
        response = table.query(
            IndexName=gsi_name, 
            KeyConditionExpression=Key('user_id').eq(user_id) &
                                   Key('created_at').between(start_date.isoformat(), end_date.isoformat()),
            ScanIndexForward=False 
        )

        posts = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'posts': posts,
                'count': len(posts)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
