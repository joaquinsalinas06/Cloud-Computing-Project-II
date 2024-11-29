import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    gsi_name = os.environ['GSI']

    user_id = event['path']['user_id']
    start_created_at = event['query']['start_created_at']
    end_created_at = event['query']['end_created_at']


    if not user_id or not start_created_at or not end_created_at:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: user_id, start_created_at, end_created_at'})
        }

    try:
        start_date = datetime.strptime(start_created_at, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_created_at, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid date format. Expected YYYY-MM-DD HH:MM:SS'})
        }

    try:
        response = table.query(
            IndexName=gsi_name, 
            KeyConditionExpression=Key('user_id').eq(user_id) &
                                   Key('created_at').between(start_date.isoformat(), end_date.isoformat()),
            ScanIndexForward=False 
        )

        posts = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'posts': posts,
                'count': len(posts)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
