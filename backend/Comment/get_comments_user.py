import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda handler to get paginated comments for a specific user and provider.
    Supports pagination using page number and page size parameters.
    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    query_params = event.get('query', {}) or {}

    # Get user_id and provider_id from path/query parameters
    user_id = int(event['path']['user_id'])
    provider_id = event['query']['provider_id']
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
        
    # Query parameters for DynamoDB
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query_params = {
            'IndexName': 'user-date-index',
            'KeyConditionExpression': Key('user_id').eq(user_id) & Key('date').between(start_date.isoformat(), end_date.isoformat()),
            'ScanIndexForward': False,  # Sort in descending order (newest first)
        }
        
        response = table.query(**query_params)
        comment_ids = [item['comment_id'] for item in response.get('Items', [])]

        # Second query to get comments with the specific comment_ids and provider_id
        all_items = []
        for comment_id in comment_ids:
            comment_params = {
                'TableName': table.name,
                'KeyConditionExpression': Key('provider_id').eq(provider_id) & Key('comment_id').eq(comment_id)
            }
            comment_response = table.query(**comment_params)
            all_items.extend(comment_response.get('Items', []))
    else:
        query_params = {
            'IndexName': 'provider-user-index',
            'KeyConditionExpression': Key('user_id').eq(user_id) & Key('provider_id').eq(provider_id),
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
