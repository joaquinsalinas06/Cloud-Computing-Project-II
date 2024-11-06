import boto3
import hashlib
import secrets
import os
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    provider_id = event.get('provider_id')
    email = event.get('email')
    password = event.get('password')
    hashed_password = hash_password(password)
    
    dynamodb = boto3.resource('dynamodb')
    user_table_name = os.getenv('TABLE_NAME_e')
    token_table_name = os.getenv('TABLE2_NAME_e')
    
    user_table = dynamodb.Table(user_table_name)
    token_table = dynamodb.Table(token_table_name)
    
    response = user_table.get_item(
        Key={
            'provider_id': provider_id,
            'email': email
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Usuario no existe'
        }
    else:
        hashed_password_bd = response['Item']['password']
        if hashed_password == hashed_password_bd:
            token = secrets.token_hex(32)
            token_table.put_item(
                Item={
                    'provider_id': provider_id,
                    'email': email,
                    'token': token,
                    'expiration': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }
    
    return {
        'statusCode': 200,
        "token": token
    }