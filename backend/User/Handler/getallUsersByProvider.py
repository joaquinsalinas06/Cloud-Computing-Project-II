import boto3
import os
import json

def lambda_handler(event, context):
    try:
        # Obtener el provider_id desde el path
        provider_id = event['path']['provider_id']

        # Obtener parámetros de consulta
        query_params = event.get('query', {}) or {}
        page = int(query_params.get('page', '1'))
        limit = int(query_params.get('limit', '10'))
        
        page = max(page, 1)
        limit = min(max(limit, 1), 50) 

        token = event['headers']['Authorization']
        payload = json.dumps({"token": token})
        lambda_client = boto3.client('lambda')
        invoke_response = lambda_client.invoke(
            FunctionName='api-mure-user-dev-validateToken',
            InvocationType='RequestResponse',
            Payload=payload
        )
        
        response_payload = json.loads(invoke_response['Payload'].read())
        print("Response Payload:", response_payload) 
        
        if response_payload.get('statusCode') != 200:
            error_message = response_payload.get('body', {}).get('error', 'Unknown error')
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized', 'message': error_message})
            }

        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv('TABLE_NAME_e')
        table = dynamodb.Table(table_name)

        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id),
            Limit=limit,
        )

        items = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')

        while 'LastEvaluatedKey' in response and len(items) < limit:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id),
                Limit=limit - len(items),
                ExclusiveStartKey=last_evaluated_key
            )
            items.extend(response.get('Items', []))
            last_evaluated_key = response.get('LastEvaluatedKey')
        
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No users found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'users': items})
        }

    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
