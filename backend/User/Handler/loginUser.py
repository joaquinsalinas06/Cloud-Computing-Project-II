import boto3
import hashlib
import secrets

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    provider_id = event.get('provider_id')
    email = event['email']
    password = event['password']
    hashed_password = hash_password(password)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('mure_user')
    response = table.get_item(
        Key={
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
            table.update_item(
                Key={
                    'email': email
                },
                UpdateExpression="set token = :t",
                ExpressionAttributeValues={
                    ':t': token
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