import boto3
import os
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    """
    Lambda handler to retrieve paginated users for a specific provider.
    Supports pagination using page number and page size parameters.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv('TABLE_NAME'))

    try:
        provider_id = event['path']['provider_id']
        token = event['headers']['Authorization']
        
        if not provider_id or not token:
            return {
                'statusCode': 400,
                'body': {'error': 'Missing parameters or token'}
            }

        payload = '{ "token": "' + token +  '" }'        
        lambda_client = boto3.client('lambda')
        invoke_response = lambda_client.invoke(
            FunctionName='api-mure-user-dev-validateToken',
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
        
        query_params = event.get('query', {}) or {}
        
        page = int(query_params.get('page', '1'))
        page_size = int(query_params.get('pageSize', '10'))
        
        if page < 1:
            page = 1
        if page_size > 50:  
            page_size = 50
        if page_size < 1:
            page_size = 10
        
        query_params = {
            'KeyConditionExpression': Key('provider_id').eq(provider_id),
            'Limit': page_size,
            'ScanIndexForward': False  
        }

        start_index = (page - 1) * page_size

        count_response = table.query(
            KeyConditionExpression=Key('provider_id').eq(provider_id),
            Select='COUNT'
        )
        total_items = count_response['Count']
        total_pages = (total_items + page_size - 1) // page_size

        if start_index > 0:
            paginator = table.meta.client.get_paginator('query')
            operation_params = {
                'TableName': table.name,
                'KeyConditionExpression': Key('provider_id').eq(provider_id),
                'ScanIndexForward': False,
            }

            all_items = []
            for page_response in paginator.paginate(**operation_params):
                all_items.extend(page_response['Items'])
                if len(all_items) >= start_index + page_size:
                    break

            items = all_items[start_index:start_index + page_size]
        else:
            response = table.query(**query_params)
            items = response.get('Items', [])

        users = []
        for item in items:
            users.append({
                'user_id': item['user_id'],
                'email': item['email'],
                'username': item['username'],
                'provider_id': item['provider_id'],
                'data': item['data']
            })
        
        pagination = {
            'currentPage': page,
            'pageSize': page_size,
            'totalItems': total_items,
            'totalPages': total_pages,
            'hasNextPage': page < total_pages,
            'hasPreviousPage': page > 1
        }
        
        result = {
            'users': users,
            'pagination': pagination,
            'provider_id': provider_id,
            'total_users': total_items
        }
        
        return {
            'statusCode': 200,
            'body': (result)
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input', 'message': str(ve)})
        }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'message': str(e)})
        }
