import boto3
import os
import json

def lambda_handler(event, context):
    user_id = event['path']['user_id']
    provider_id = event['path']['provider_id']
    token = event['headers']['Authorization']
    
    lambda_client = boto3.client('lambda')
    payload = {
        "token": token
    }
    
    invoke_response = lambda_client.invoke(
        FunctionName=os.getenv('AUTHORIZER_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    response_payload = json.load(invoke_response['Payload'])
    print(response_payload)  
    
    if invoke_response['StatusCode'] != 200 or response_payload.get('statusCode') != 200:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    table_name = os.getenv('TABLE_NAME_e')
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
                'body': json.dumps({'error': 'User not found'})
            }
        
        datos = event['body']('data')
        if datos:
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in datos.items():
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
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User updated'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Data not provided'})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing parameters'})
        }
