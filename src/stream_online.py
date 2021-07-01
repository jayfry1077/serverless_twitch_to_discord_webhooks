import json
import os
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from shared.discord_utils import call_discord


STAGE = os.environ.get('STAGE', 'dev')
logger = Logger(service='stream-online-event-handler')
discord_callback_url = parameters.get_parameter(
    f'/{STAGE}/discord/callback', decrypt=True)


def main(event, context):

    call_discord(discord_callback_url, event['detail']['event'])
