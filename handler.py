import json
import hmac
import hashlib
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
import os
import requests

logger = Logger(service='twitch-discord-callback')

STAGE = os.environ.get('STAGE', 'dev')
webhook_secret = parameters.get_parameter(
    f'/{STAGE}/twitch/webhook/secret', decrypt=True)
discord_callback_url = parameters.get_parameter(
    f'/{STAGE}/discord/callback', decrypt=True)


def call_discord(discord_webhook, data):
    res = requests.post(discord_webhook, json=data, headers={
                        'Content-type': 'application/json'})
    print('Response ' + res.text)


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

    call_discord(discord_callback_url, {
                 "content": "@everyone\nEmjayInk went live on twitch!\nhttps://www.twitch.tv/emjayink"})

    return event_body['challenge']
