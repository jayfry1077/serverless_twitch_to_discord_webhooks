import requests
from aws_lambda_powertools import Logger

logger = Logger(service='guilded-utils')


def call_guilded(webhook_url=str, title=str, description=str, stream_url=str, image_url=str) -> None:

    guilded_body = {'title': title,
                    'url': stream_url, 'image': {'url': image_url}, 'description': description}

    try:
        res = requests.post(webhook_url, json={'embeds': [guilded_body]}, headers={
                            'Content-type': 'application/json'})
        logger.info('Response ' + res.text)
    except Exception as e:
        logger.error(f'Error while making discord call: {e}')
