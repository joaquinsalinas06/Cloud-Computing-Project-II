import boto3
import os

def lambda_handler(event, context):
    provider_id = event['pathParameters']['provider_id']
    page = int(event['queryStringParameters'].get('page', 1))
    limit = int(event['queryStringParameters'].get('limit', 10))
    
    dynamodb = boto3.resource('dynamodb')
    table_name = os.getenv('TABLE_NAME_e')
    table = dynamodb.Table(table_name)
    
    offset = (page - 1) * limit
    
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id),
        Limit=limit,
        ExclusiveStartKey={'provider_id': provider_id, 'user_id': offset} if offset > 0 else None
    )
    
    if 'Items' not in response or len(response['Items']) == 0:
        return {
            'statusCode': 404,
            'body': 'No users found'
        }
    
    return {
        'statusCode': 200,
        'body': response['Items']
    }