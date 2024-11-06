import boto3
import os

def lambda_handler(event, context):
    user_id = event['pathParameters']['user_id']
    provider_id = event['pathParameters']['provider_id']
    table_name = os.getenv('TABLE_NAME_e')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    if provider_id and user_id:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('provider_id').eq(provider_id) & boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'body': 'User not found'
            }
        else:
            datos = event.get('data')
            if datos:
                expresion = "SET "
                expression_attribute_values = {}
                for key, value in datos.items():
                    expresion += f"{key} = :{key}, "
                    expresion[f":{key}"] = value
                expresion = expresion.rstrip(", ")

                table.update_item(
                    Key={
                        'provider_id': provider_id,
                        'user_id': user_id
                    },
                    UpdateExpression=expresion,
                    ExpressionAttributeValues=expression_attribute_values
                )
                return {
                    'statusCode': 200,
                    'body': 'User updated'
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Data not provided'
                }
    else:
        return {
            'statusCode': 400,
            'body': 'Missing parameters'
        }