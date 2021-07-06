import boto3
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
DISCORD_CALLBACKS_TABLE = os.environ.get('DISCORD_CALLBACKS_TABLE')
table = dynamodb.Table(DISCORD_CALLBACKS_TABLE)


def get_callbacks(streamer_id=str) -> list:

    try:
        response = table.get_item(
            Key={'PK': streamer_id},
            ProjectionExpression='callbacks'
        )

        if 'Item' not in response.keys():
            raise Exception(f'No callbacks for user {streamer_id}')

        if len(response['Item']['callbacks']) == 0:
            raise Exception(f'No callbacks for user {streamer_id}')

        return response['Item']['callbacks']

    except ClientError as e:
        raise Exception(f'Error while getting callback: {e}')
