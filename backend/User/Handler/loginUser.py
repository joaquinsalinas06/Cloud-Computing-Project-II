import boto3
import hashlib
import secrets
import os
import json
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    provider_id = event['body']['provider_id']
    email = event['body']['email']
    password = event['body']['password']
    hashed_password = hash_password(password)

    user_table_name = os.environ['TABLE_NAME']
    token_table_name = os.environ['TABLE2_NAME']
    provider_email_index = os.environ['INDEXLSI1_TABLE1_NAME']

    dynamodb = boto3.resource('dynamodb')
    user_table = dynamodb.Table(user_table_name)
    token_table = dynamodb.Table(token_table_name)

    response = user_table.query(
        IndexName=provider_email_index,
        KeyConditionExpression=Key('provider_id').eq(provider_id) & Key('email').eq(email)
    )

    if 'Items' not in response or not response['Items']:
        return {
            'statusCode': 403,
            'body': {
                'status': 'error',
                'message': 'User does not exist'
            }
        }

    user = response['Items'][0]
    hashed_password_bd = user['password']
    user_id_response = user['user_id']
    
    if hashed_password != hashed_password_bd:
        return {
            'statusCode': 403,
            'body': json.dumps({
                'status': 'error',
                'message': 'Incorrect password'
            })
        }

    token_response = token_table.query(
        KeyConditionExpression=Key('provider_id').eq(provider_id) & Key('user_id').eq(user_id_response)
    )

    if 'Items' in token_response and token_response['Items']:
        token_item = token_response['Items'][0]
        expiration_str = token_item['expiration']
        expiration = datetime.strptime(expiration_str, '%Y-%m-%d %H:%M:%S')

        if expiration > datetime.now():
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'A valid token already exists'
                })
            }
        else:
            token_table.delete_item(
                Key={
                    'provider_id': provider_id,
                    'user_id': user_id_response
                }
            )

    token = secrets.token_hex(32)
    expiration = (datetime.now() + timedelta(days=1))

    token_table.put_item(
        Item={
            'provider_id': provider_id,
            'user_id': user_id_response,
            'token': token,
            'expiration': expiration.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    return {
        'statusCode': 200,
        'body': {
            'status': 'success',
            'message': 'Authentication successful',
            'data': {
                'token': token,
                'expiration': expiration.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': user_id_response
            }
        },
        'headers': {
            'Content-Type': 'application/json'
        }
    }
