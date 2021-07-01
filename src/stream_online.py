import os
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from shared.discord_utils import call_discord
from shared.twitch_utils import get_live_stream_info


STAGE = os.environ.get('STAGE', 'dev')
logger = Logger(service='stream-online-event-handler')
discord_callback_url = parameters.get_parameter(
    f'/{STAGE}/discord/callback', decrypt=True)


def main(event, context):

    broadcaster_id = event['detail']['event']['broadcaster_user_id']
    broadcaster_name = event['detail']['event']['broadcaster_user_name']
    broadcaster_url_id = event['detail']['event']['broadcaster_user_login']

    logger.info(
        f'Streamer [{broadcaster_name}] went live, sending discord notification')

    try:
        live_stream_info = get_live_stream_info(broadcaster_id)
        title = ''
        # To handle the usecase where a streamer goes live, but we were unable to retrieve their stream title for some reason.
        if len(live_stream_info) != 0:
            title = live_stream_info["title"]

        discord_message = f':red_circle: {broadcaster_name} is live!\n{title}\nhttps://www.twitch.tv/{broadcaster_url_id}'

        call_discord(discord_callback_url, discord_message)

    except Exception as e:
        logger.error(e)
