import json
import os
import decimal
import boto3
from boto3.dynamodb.conditions import Key,Attr
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda handler to get paginated comments for a specific post.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    query_params = event.get('query', {}) or {}

    ####
    token = event['headers']['Authorization']
    token_function = os.environ['LAMBDA_FUNCTION_NAME']    
    
    lambda_client = boto3.client('lambda')
    payload = '{ "token": "' + token +  '" }'
    
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
    
    ###########
    
    # Get path and query parameters
    post_id = int(event['path']['post_id'])
    provider_id = event['query']['provider_id']

    start_date = query_params.get('start_date')
    end_date = query_params.get('end_date')
    
    # Get pagination parameters from query parameters
    page = int(query_params.get('page', '1'))
    page_size = int(query_params.get('pageSize', '10'))
    
    # Basic parameter validation
    page = max(1, page)
    page_size = max(1, min(50, page_size))  # Limit page size between 1 and 50
    
    provider_post_index = os.environ['LSI1']
    
    if start_date and end_date:
        # Query parameters
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        query_params = {
            'IndexName': provider_post_index,
            'KeyConditionExpression': Key('provider_id').eq(provider_id) & Key('post_id').eq(post_id),
            'FilterExpression': Attr('date').between(start_date.isoformat(), end_date.isoformat()),
            'ScanIndexForward': False  # Sort in descending order
        }
    else:
    # Query parameters
        query_params = {
            'IndexName': provider_post_index,
            'KeyConditionExpression': Key('provider_id').eq(provider_id) & Key('post_id').eq(post_id),
            'ScanIndexForward': False  # Sort in descending order
        }
    
    # Get total count
    count_response = table.query(
        **query_params,
        Select='COUNT'
    )
    total_items = count_response['Count']
    total_pages = (total_items + page_size - 1) // page_size
    
    # Calculate pagination
    start_index = (page - 1) * page_size
    query_params['Limit'] = page_size
    
    # Get items for current page
    if start_index > 0:
        # Need to scan to the starting point
        response = table.query(**query_params)
        items = response.get('Items', [])[start_index:start_index + page_size]
    else:
        # First page can be queried directly
        response = table.query(**query_params)
        items = response.get('Items', [])
    
    # Format comments
    comments = [{
        'comment_id': item['comment_id'],
        'user_id': item['user_id'],
        'text': item['text'],
        'date': item['date']
    } for item in items]
    
    # Prepare response
    result = {
        'comments': comments,
        'pagination': {
            'currentPage': page,
            'pageSize': page_size,
            'totalItems': total_items,
            'totalPages': total_pages,
            'hasNextPage': page < total_pages,
            'hasPreviousPage': page > 1
        }
    }
    
    return result
    
