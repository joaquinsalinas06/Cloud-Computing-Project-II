import boto3
import os

import boto3.dynamodb

def lambda_handler(event, context):
    provider_id = event['pathParameters']['provider_id']
    user_id = event['pathParameters']['user_id']
    dynamodb = boto3.resource('dynamodb')
    dynamodb = boto3.dynamodb.resource('dynamodb') 
    user_table_name = os.getenv('TABLE_NAME_e')
    user_table = dynamodb.Table(user_table_name)
    response = user_table.get_item(
        key = {
            'provider_id': provider_id,
            'user_id': user_id
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'User doesn\'t exist'
        }
    else:
        user = response['Item']
