import json
import hmac
import hashlib
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
import os
import boto3

logger = Logger(service='twitch-discord-callback')

STAGE = os.environ.get('STAGE', 'dev')
EVENT_BUS = f'serverless-twitch-to-discord-webhooks-{STAGE}'
webhook_secret = parameters.get_parameter(
    f'/{STAGE}/twitch/webhook/secret', decrypt=True)

event_bridge = boto3.client('events')


def send_event_bridge_event(event_body):

    source = json.loads(event_body)

    event = [{
        'Source': source['subscription']['type'],
        'DetailType': 'twitch',
        'Detail': event_body,
        'EventBusName': EVENT_BUS
    }]
    try:
        event_bridge.put_events(Entries=event)
    except Exception as e:
        logger.error(e)


def valid_signature(headers, event_body):
    message_id = headers['twitch-eventsub-message-id']
    message_timestamp = headers['twitch-eventsub-message-timestamp']
    message_signature = headers['twitch-eventsub-message-signature']

    hmac_message = message_id + message_timestamp + event_body

    key = bytes(webhook_secret, 'utf-8')
    data = bytes(hmac_message, 'utf-8')

    signature = hmac.new(key, data, hashlib.sha256)

    expected_signature_header = 'sha256=' + signature.hexdigest()

    logger.info(f'Expected: {expected_signature_header}')
    logger.info(f'Actual: {message_signature}')

    if message_signature != expected_signature_header:
        return False

    return True


def online(event, context):

    print(event)

    headers = event['headers']
    event_body = json.loads(event['body'])

    if not valid_signature(headers, event['body']):
        logger.error('Signature mistach.')
        return {"statusCode": 403}

    if headers['twitch-eventsub-message-type'] == 'webhook_callback_verification':
        return event_body['challenge']

    # Not going to send a failure to twitch if the event put fails
    try:
        send_event_bridge_event(event['body'])
    except:
        return {"statusCode": 200}

    return {"statusCode": 200}
