from shared.discord_utils import call_discord
import json
import os
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger

STAGE = os.environ.get('STAGE', 'dev')
logger = Logger(service='twitch-event-handler')
discord_callback_url = parameters.get_parameter(
    f'/{STAGE}/discord/callback', decrypt=True)


class stream_online():
    def __init__(self, event) -> None:
        self.event = event

    def execute(self):
        call_discord(discord_callback_url, self.event['event'])
