import boto3
import os

def lambda_handler(event, context):
    provider_id = event['pathParameters']['provider_id']
    user_id = event['pathParameters']['user_id']
    
    dynamodb = boto3.resource('dynamodb')
    user_table_name = os.getenv('TABLE_NAME_e')
    user_table = dynamodb.Table(user_table_name)
    
    response = user_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & boto3.dynamodb.conditions.Key('user_id').eq(user_id)
    )
    
    if 'Items' not in response or len(response['Items']) == 0:
        return {
            'statusCode': 404,
            'body': 'User not found'
        }
    
    return {
        'statusCode': 200,
        'body': response['Items'][0]
    }