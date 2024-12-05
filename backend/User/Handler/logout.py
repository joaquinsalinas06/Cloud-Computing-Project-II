import boto3
import os
import json

def lambda_handler(event, context):
    provider_id = event['body']['provider_id']
    user_id = int(event['body']['user_id'])  
    token = event['headers']['Authorization']
    
    if not token:
        return {
            'statusCode': 400,
            'body':{
                'status': 'error',
                'message': 'Authorization token is missing'
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
    token_table_name = os.environ['TABLE2_NAME']  
    token_index_name = os.environ['LSI2']  
    
    dynamodb = boto3.resource('dynamodb')  
    token_table = dynamodb.Table(token_table_name)

    try:
        
        response = token_table.query(
            IndexName=token_index_name, 
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('token').eq(token)
        )

        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 401,
                'body':{
                    'status': 'error',
                    'message': 'Invalid or expired authorization token'
                },
                'headers': {
                    'Content-Type': 'application/json'
                }
            }

        token_response = token_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )

        if 'Items' in token_response and len(token_response['Items']) > 0:
            for item in token_response['Items']:
                token_table.delete_item(
                    Key={
                        'provider_id': item['provider_id'],  
                        'user_id': item['user_id']  
                    }
                )

        return {
            'statusCode': 200,
            'body': {
                'status': 'success',
                'message': 'All tokens deleted successfully, logout complete'
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'status': 'error',
                'message': f'Error occurred: {str(e)}'
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }
