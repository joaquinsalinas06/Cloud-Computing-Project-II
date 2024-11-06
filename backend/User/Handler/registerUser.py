import boto3
import hashlib
import os
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        provider_id = event.get('provider_id')
        user_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        password = event.get('password')
        email = event.get('email')
        username = event.get('username')
        data = event.get('data')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        telefono = data.get('telefono')
        fecha_nacimiento = data.get('fecha_nacimiento')
        genero = data.get('genero')
        active = 'true'
        datecreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        edad = data.get('edad')
        hashed_password = hash_password(password)
        
        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv('TABLE_NAME_e')
        table = dynamodb.Table(table_name)
        
        existentes = table.get_item(
            Key={
                'provider_id': provider_id,
                'email': email
            }
        )
        if 'Item' in existentes:
            mensaje = {
                'error': 'User already exists'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

        if user_id and password and provider_id and email and username and data:
            t_usuarios = dynamodb.Table(table_name)
            t_usuarios.put_item(
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
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing user_id or password'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }
    except Exception as e:
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }