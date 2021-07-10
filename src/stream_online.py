import os
from aws_lambda_powertools import Logger
from shared.twitch_utils import get_live_stream_info, get_streamer_info
from shared.dynamo_utils import get_callbacks
from factory.callbacks import CallbackFactory
import requests


STAGE = os.environ.get('STAGE', 'dev')
logger = Logger(service='stream-online-event-handler')


def main(event, context):
    logger.info(event)

    broadcaster_id = event['detail']['event']['broadcaster_user_id']
    callbacks = get_callbacks(broadcaster_id)

    broadcaster_name = event['detail']['event']['broadcaster_user_name']
    broadcaster_url_id = event['detail']['event']['broadcaster_user_login']
    profile_image_url = get_streamer_info(broadcaster_url_id)

    logger.info(
        f'Streamer [{broadcaster_name}] went live, sending notification(s)')

    for callback in callbacks:
        try:
            live_stream_info = get_live_stream_info(broadcaster_id)

            broadcaster = {'broadcaster_id': broadcaster_id, 'broadcaster_name': broadcaster_name,
                           'broadcaster_url_id': broadcaster_url_id, 'profile_image_url': profile_image_url[0]['profile_image_url'],
                           'callback': callback, 'live_stream_info': live_stream_info}

            callback_message = CallbackFactory().serialize(broadcaster)

            response = requests.post(callback['url'], json=callback_message, headers={
                'Content-type': 'application/json'})

            logger.info('Response ' + response.text)

        except Exception as e:
            logger.error(e)
