import json
import os
import decimal
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    """
    Lambda handler to get paginated comments for a specific post.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    try:
        # Get path and query parameters
        post_id = int(event['path']['post_id'])
        provider_id = event['query']['provider_id']
        
        # Get pagination parameters with defaults
        page = int(event.get('query', {}).get('page', '1'))
        page_size = int(event.get('query', {}).get('pageSize', '10'))
        
        # Basic parameter validation
        page = max(1, page)
        page_size = max(1, min(50, page_size))  # Limit page size between 1 and 50
        
        # Query parameters
        query_params = {
            'IndexName': 'provider-post-index',
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
            'date': item['date'],
            'post_id': item['post_id']
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
        
    except (ValueError, TypeError) as e:
        return e
    except Exception as e:
        return e