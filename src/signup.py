from aws_lambda_powertools import Logger
from shared.discord_utils import valid_signature
import os
import json
import boto3


logger = Logger(service='signup')
STAGE = os.environ.get('STAGE', 'dev')
DISCORD_PING_PONG = {'statusCode': 200, "headers": {
    "content-type": 'application/json'}, 'body': json.dumps({"type": 1})}
EVENT_BUS = f'serverless-twitch-to-discord-webhooks-{STAGE}'
event_bridge = boto3.client('events')


def discord_body(status_code=int, type=int, message=str):
    return {
        "statusCode": status_code,
        "headers": {"content-type": 'application/json'},
        'body': json.dumps({"type": type,
                            "data": {
                                "tts": False,
                                "content": message}})
    }


def send_event_bridge_event(event_body):

    source = f"discord.{event_body['data']['options'][0]['name']}"

    event = [{
        'Source': source,
        'DetailType': 'discord',
        'Detail': json.dumps(event_body),
        'EventBusName': EVENT_BUS
    }]
    try:
        event_bridge.put_events(Entries=event)
    except Exception as e:
        logger.error(e)


def main(event, context):
    print(event)

    if not valid_signature(event):
        return discord_body(400, 2, 'Error Validating Discord Signature')

    body = json.loads(event['body'])

    if body['type'] == 1:
        return DISCORD_PING_PONG

    try:
        send_event_bridge_event(body)
        return discord_body(200, 5, '')
    except Exception as e:
        logger.error(e)
        return discord_body(200, 4, 'Something went wrong')


# main('', '')
