import boto3
import os
import json

def lambda_handler(event, context):
    try:
        provider_id = event['path']['provider_id']
   
        query_params = event.get('query', {}) or {}

        page = int(query_params.get('page', '1'))
        limit = int(query_params.get('pageSize', '10'))
        
        if page < 1:
            page = 1
        if limit > 50:  
            limit = 50
        if limit < 1:
            limit = 10
        token = event['headers']['Authorization']  
        
        lambda_client = boto3.client('lambda')
        
        payload = {
            "provider_id": provider_id,
            "token": token
        }
        
        invoke_response = lambda_client.invoke(
            FunctionName=os.getenv('AUTHORIZER_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.load(invoke_response['Payload'])
        
        if invoke_response['StatusCode'] != 200 or response_payload.get('authorized') != True:
            return {
                'statusCode': 401,
                'body': {'error': 'Unauthorized'}
            }

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
                'body': {'error': 'No users found'}
            }

        return {
            'statusCode': 200,
            'body': {'users': response['Items']}
        }

    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': f"Internal server error: {str(e)}"}
        }
