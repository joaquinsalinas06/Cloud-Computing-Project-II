import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Lambda handler to get paginated comments for a specific user within a date range.
    Supports pagination using page number and page size parameters.
    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    # Get user_id, provider_id, start_date, and end_date from path/query parameters
    user_id = int(event['path']['user_id'])
    provider_id = event['query']['provider_id']
    start_date = datetime.strptime(event['query']['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(event['query']['end_date'], '%Y-%m-%d')

    # Get pagination parameters from query parameters
    query_params = event.get('query', {}) or {}
    page = int(query_params.get('page', '1'))
    page_size = int(query_params.get('pageSize', '10'))

    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size > 50:  # Maximum page size of 50
        page_size = 50
    if page_size < 1:
        page_size = 10

    # Query parameters for DynamoDB (user-date-index)
    user_date_query_params = {
        'IndexName': 'user-date-index',
        'KeyConditionExpression': Key('user_id').eq(user_id) & Key('date').between(start_date.isoformat(), end_date.isoformat()),
        'ProjectionExpression': 'comment_id',
        'Limit': page_size * 2,  # Fetch extra to handle pagination
        'ScanIndexForward': False,
    }

    # First, get the matching comment_ids and provider_ids
    comment_ids = []
    paginator = table.meta.client.get_paginator('query')
    for page_response in paginator.paginate(**user_date_query_params):
        comment_ids.extend([item['comment_id'] for item in page_response['Items']])
    # Query parameters for DynamoDB (table)
    table_query_params = {
        'KeyConditionExpression': Key('provider_id').eq(provider_id) & Key('comment_id').in_(comment_ids),
        'Limit': page_size,
        'ScanIndexForward': False,
    }

    # Query the table with pagination
    all_items = []
    paginator = table.meta.client.get_paginator('query')
    for page_response in paginator.paginate(**table_query_params):
        all_items.extend(page_response['Items'])
        if len(all_items) >= (page - 1) * page_size + page_size:
            break

    # Calculate pagination values
    start_index = (page - 1) * page_size
    total_items = len(all_items)
    total_pages = (total_items + page_size - 1) // page_size

    # Format the comments
    comments = []
    for item in all_items[start_index:start_index + page_size]:
        comments.append({
            'comment_id': item['comment_id'],
            'text': item['text'],
            'date': item['date'],
            'post_id': item['post_id']
        })

    # Prepare pagination metadata
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
        'provider_id': provider_id,
        'total_comments': total_items
    }

    return result