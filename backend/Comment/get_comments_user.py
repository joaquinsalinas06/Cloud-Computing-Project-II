import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from datetime import datetime


def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    query_params = event.get('query', {}) or {}
    
    
    ################
    token = event['headers']['Authorization']
    token_function = os.environ['LAMBDA_FUNCTION_NAME']  

    provider_id = event['path']['provider_id']  
        
    
    lambda_client = boto3.client('lambda')
    payload = json.dumps({
            'token': token,
            'provider_id': provider_id
        })    
    
    invoke_response = lambda_client.invoke(
        FunctionName=token_function,
        InvocationType='RequestResponse',
        Payload=payload
    )
    
    response_payload = json.loads(invoke_response['Payload'].read())
    print("Response Payload:", response_payload)
    
    if 'statusCode' not in response_payload or response_payload['statusCode'] != 200:
        error_message = response_payload.get('body', {}).get('error', 'Unknown error')
        return {
            'statusCode': 401,
            'body': {'error': 'Unauthorized', 'message': error_message}
        }

    #################

    # Get user_id and provider_id from path/query parameters
    user_id = int(event['path']['user_id'])
    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')

    # Get pagination parameters from query parameters
    page = int(query_params.get('page', '1'))
    page_size = int(query_params.get('pageSize', '10'))
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size > 50:  # Maximum page size of 50
        page_size = 50
    if page_size < 1:
        page_size = 10
        
    user_date_index = os.environ['GSI'] 
    # Query parameters for DynamoDB
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        query_params = {
            'IndexName': user_date_index, 
            'KeyConditionExpression': Key('user_id').eq(user_id) & Key('date').between(start_date.isoformat(), end_date.isoformat()),
            'FilterExpression': Attr('provider_id').eq(provider_id),
            'ScanIndexForward': False,  # Sort in descending order (newest first)
        }
        response = table.query(**query_params)
        all_items = response.get('Items', [])
    else:
        query_params = {
            'IndexName': user_date_index,
            'KeyConditionExpression': Key('user_id').eq(user_id),
            'FilterExpression': Attr('provider_id').eq(provider_id),
            'ScanIndexForward': False  # Sort in descending order
        }
        response = table.query(**query_params)
        all_items = response.get('Items', [])
    
    # Apply pagination
    start_index = (page - 1) * page_size
    items = all_items[start_index:start_index + page_size]
    
    # Format the comments
    comments = []
    for item in items:
        comments.append({
            'comment_id': item['comment_id'],
            'text': item['text'],
            'date': item['date'],
            'post_id': item['post_id'],
            'provider_id': item['provider_id']})
        
    # Prepare pagination metadata
    total_items = len(all_items)
    total_pages = (total_items + page_size - 1) // page_size
    pagination = {
        'currentPage': page,
        'pageSize': page_size,
        'totalItems': total_items,
        'totalPages': total_pages,
        'hasNextPage': page < total_pages,
        'hasPreviousPage': page > 1
    }
        
    # Prepare the response
    result = {
        'comments': comments,
        'pagination': pagination,
        'user_id': user_id,
        'total_comments': total_items
    }
        
    return result
