import boto3
import os

def lambda_handler(event, context):
    user_id = event['pathParameters']['user_id']
    provider_id = event['pathParameters']['provider_id']
    user_table_name = os.getenv('TABLE_NAME_e')
    token_table_name = os.getenv('TABLE2_NAME_e')
    
    dynamodb = boto3.resource('dynamodb')
    user_table = dynamodb.Table(user_table_name)
    token_table = dynamodb.Table(token_table_name)
    
    if provider_id and user_id:
        response = user_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': 'User not found'
            }
        else:
            user_table.delete_item(
                Key={
                    'provider_id': provider_id,
                    'user_id': user_id
                }
            )
            
            token_response = token_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            if 'Items' in token_response:
                for item in token_response['Items']:
                    token_table.delete_item(
                        Key={
                            'provider_id': provider_id,
                            'user_id': user_id,
                            'token': item['token']
                        }
                    )
            
            return {
                'statusCode': 200,
                'body': 'User and associated tokens deleted'
            }
    else:
        return {
            'statusCode': 400,
            'body': 'Missing parameters'
        }