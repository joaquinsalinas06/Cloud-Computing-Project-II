import boto3
import os
import json

def lambda_handler(event, context):
    user_id = event['path']['user_id']
    provider_id = event['path']['provider_id']
    token = event['headers']['Authorization']
    user_id = int(user_id)
    
    lambda_client = boto3.client('lambda')
    payload = json.dumps({
        'token': token,
        'provider_id': provider_id
    })
    token_function = os.environ['AUTHORIZER_FUNCTION_NAME']

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
        
    table_name = os.environ['TABLE_NAME']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    if provider_id and user_id:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & 
                                   boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': {'error': 'User not found'}
            }
        
        body_content = event['body']
        if isinstance(body_content, str):
            body_content = json.loads(body_content)
        
        if body_content:
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in body_content.items():
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
            
            update_expression = update_expression.rstrip(", ")

            table.update_item(
                Key={
                    'provider_id': provider_id,
                    'user_id': user_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            
            updated_user = table.get_item(
                Key={
                    'provider_id': provider_id,
                    'user_id': user_id
                }
            ).get('Item', {})
            
            if updated_user:
                if 'password' in updated_user:
                    del updated_user['password']
                
                return {
                    'statusCode': 200,
                    'body': {
                        'message': 'User updated',
                        'updated_user': updated_user
                    }
                }
            else:
                return {
                    'statusCode': 404,
                    'body': {'error': 'User not found after update'}
                }
        else:
            return {
                'statusCode': 400,
                'body': {'error': 'No data provided for update'}
            }
    else:
        return {
            'statusCode': 400,
            'body': {'error': 'Missing parameters'}
        }
