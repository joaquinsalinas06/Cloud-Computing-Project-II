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
    provider_id = event.get('provider_id')
    email = event.get('email')
    password = event.get('password')
    hashed_password = hash_password(password)

    user_table_name = os.getenv('TABLE_NAME_e')
    token_table_name = os.getenv('TABLE2_NAME_e')
    provider_email_index = os.getenv('INDEXLSI1_TABLE1_NAME_e')

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
            'body': json.dumps({'error': 'Usuario no existe'})
        }

    user = response['Items'][0]
    hashed_password_bd = user['password']
    
    if hashed_password == hashed_password_bd:
        token = secrets.token_hex(32)
        expiration = int((datetime.now() + timedelta(days=1)).timestamp())
        token_table.put_item(
            Item={
                'provider_id': provider_id,
                'email': email,
                'token': token,
                'expiration': expiration
            }
        )
    else:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Password incorrecto'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'token': token})
    }
