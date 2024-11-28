import boto3
import hashlib
import os
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['TABLE_NAME']
    index_name = os.environ['LSI1']
    table = dynamodb.Table(table_name)
        
    try:

        provider_id = event['body']['provider_id']
        password = event['body']['password']
        email = event['body']['email']
        username = event['body']['username']

        if not all([provider_id, password, email, username]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        response = table.query(
            KeyConditionExpression=Key('provider_id').eq(provider_id),
            ScanIndexForward=False,  
            Limit=1  
        )
        highestUserId  = 0

        if 'Items' in response and response['Items']:
            highestUserId = int(response['Items'][0]['user_id'])


        user_id = highestUserId + 1        
        nombre = event['body']['name']
        apellido = event['body']['last_name']
        telefono = event['body']['phone_number']
        fecha_nacimiento = event['body']['birth_date']
        genero = event['body']['gender']
        edad = event['body']['age']

        active = 'true'
        datecreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hashed_password = hash_password(password)

       
        existentes = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key('provider_id').eq(provider_id) & Key('email').eq(email)
        )
        if 'Items' in existentes and existentes['Items']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'User already exists'})
            }

        table.put_item(
            Item={
                'provider_id': provider_id,
                'user_id': user_id,
                'email': email,
                'username': username,
                'password': hashed_password,
                'name': nombre,
                'last_name': apellido,
                'phone_number': telefono,
                'birth_date': fecha_nacimiento,
                'gender': genero,
                'age': edad,
                'active': active,
                'created_at': datecreated
            }
        )

        return {
            'statusCode': 200,
            'body': {
                'message': 'User registered successfully',
                'user_id': user_id
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
