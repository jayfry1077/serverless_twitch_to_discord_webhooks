import boto3
import os
from botocore.exceptions import ClientError

dynamo = boto3.client('dynamodb')
DISCORD_CALLBACKS_TABLE = os.environ.get('DISCORD_CALLBACKS_TABLE')


def get_url(streamer_id):

    try:
        response = dynamo.query(
            TableName=DISCORD_CALLBACKS_TABLE,
            KeyConditionExpression='#pk = :pk',
            ExpressionAttributeNames={
                '#pk': 'PK',
            },
            ExpressionAttributeValues={
                ':pk': {'S': streamer_id},
            }
        )

        return response['Items'][0]['callback_url']['S']

    except ClientError as e:
        raise Exception(f'Error while getting callback: {e}')
