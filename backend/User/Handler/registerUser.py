import boto3
import hashlib
import os
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        provider_id = event.get('provider_id')
        password = event.get('password')
        email = event.get('email')
        username = event.get('username')
        data = event.get('data') or {}
        
        # Validar que todos los campos requeridos están presentes
        if not all([provider_id, password, email, username]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        user_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        telefono = data.get('telefono')
        fecha_nacimiento = data.get('fecha_nacimiento')
        genero = data.get('genero')
        edad = data.get('edad')

        active = 'true'
        datecreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hashed_password = hash_password(password)

        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv('TABLE_NAME')
        index_name = os.getenv('INDEXLSI1_TABLE1_NAME')

        table = dynamodb.Table(table_name)
        
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
                'data': {
                    'nombre': nombre,
                    'apellido': apellido,
                    'telefono': telefono,
                    'fecha_nacimiento': fecha_nacimiento,
                    'genero': genero,
                    'edad': edad
                },
                'active': active,
                'datecreated': datecreated
            }
        )
        mensaje = {
            'message': 'User registered successfully',
            'user_id': user_id
        }
        return {
            'statusCode': 200,
            'body': json.dumps(mensaje)
        }
    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }