import boto3


def lambda_handler(event, context):
    provider_id = event.get('provider_id')
    user_id = event.get('user_id')

    if user_id and provider_id:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('mure_user')
        response = table.get_item(
            Key={
                'user_id': user_id,
                'provider_id': provider_id
            }
        )
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': response['Item']
            }
        else:
            return {
                'statusCode': 404,
                'body': 'User not found'
            }
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid request body: missing user_id or provider_id'
        }