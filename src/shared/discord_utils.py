import requests
from aws_lambda_powertools import Logger

logger = Logger(service='discord-utils')


def call_discord(discord_webhook=str, message=str):

    try:
        res = requests.post(discord_webhook, json={'content': message}, headers={
                            'Content-type': 'application/json'})
        logger.info('Response ' + res.text)
    except Exception as e:
        logger.error(f'Error while making discord call: {e}')
