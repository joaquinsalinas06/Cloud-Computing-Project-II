import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda handler to get paginated comments for a specific user.
    Supports pagination using page number and page size parameters.
    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    try:
        # Get user_id from path parameters
        user_id = event['pathParameters']['user_id']
        
        # Get pagination parameters from query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Parse pagination parameters with defaults
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
        query_params = {
            'IndexName': 'user-date-index',
            'KeyConditionExpression': Key('user_id').eq(user_id),
            'ScanIndexForward': False,  # Sort in descending order (newest first)
        }
        
        # First, get total count of comments for this user
        count_response = table.query(
            **query_params,
            Select='COUNT'
        )
        total_items = count_response['Count']
        total_pages = (total_items + page_size - 1) // page_size
        
        # Calculate pagination values
        start_index = (page - 1) * page_size
        
        # Add limit and offset to query
        query_params['Limit'] = page_size
        
        # If not the first page, we need to scan to the starting point
        all_items = []
        if start_index > 0:
            paginator = table.meta.client.get_paginator('query')
            operation_params = {
                'TableName': table.name,
                'IndexName': 'user-date-index',
                'KeyConditionExpression': Key('user_id').eq(user_id),
                'ScanIndexForward': False,
            }
            
            for page_response in paginator.paginate(**operation_params):
                all_items.extend(page_response['Items'])
                if len(all_items) >= start_index + page_size:
                    break
            
            items = all_items[start_index:start_index + page_size]
        else:
            # First page can be queried directly
            response = table.query(**query_params)
            items = response.get('Items', [])
            
        # Format the comments
        comments = []
        for item in items:
            comments.append({
                'comment_id': item['comment_id'],
                'user_id': item['user_id'],
                'content': item['content'],
                'date': item['date'],
                'song_id': item['song_id'],
                'song_title': item.get('song_title', ''),  # Optional field if you store song titles
                'username': item.get('username', '')  # Optional field if you store usernames
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
            'user': {
                'user_id': user_id,
                'total_comments': total_items
            }
        }
            
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Invalid pagination parameters',
                'message': str(ve)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }