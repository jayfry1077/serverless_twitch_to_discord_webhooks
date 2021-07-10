import json
from shared.twitch_utils import get_streamer_info, subscribe_to_online_events
from shared.dynamo_utils import put_subscription
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
import requests
import os


logger = Logger(service='discord-utils')
STAGE = os.environ.get('STAGE', 'dev')


def get_executor(command=str):
    if command == 'signup':
        return SignUpUser()


def update_message(application_id=str, token=str, message=str):
    url = 'https://discord.com/api/webhooks/{application_id}/{token}/messages/@original'.format(
        application_id=application_id, token=token)
    payload = {'content': message}
    headers = {'Content-Type': 'application/json'}
    response = requests.patch(url=url, headers=headers,
                              data=json.dumps(payload)).json()
    logger.info(response)
    return


class SignUpUser:
    def __init__(self) -> None:
        pass

    def set_streamer_info(self, streamer_login=str):
        self.streamer_info = get_streamer_info(streamer_login)[0]

    def subscribe_to_online(self):

        return subscribe_to_online_events(self.streamer_info['id'])

    def update_dynamo(self):

        DISCORD_CALLBACK_URL = parameters.get_parameter(
            f'/{STAGE}/discord/callback/nonmain', decrypt=True)
        GUILDED_CALLBACK_URL = parameters.get_parameter(
            f'/{STAGE}/guilded/callback/nonmain', decrypt=True)

        callbacks = [{'message': '{message}',
                      'platform': 'discord', 'url': DISCORD_CALLBACK_URL},
                     {'message': '{message}',
                      'platform': 'guilded', 'url': GUILDED_CALLBACK_URL}
                     ]

        put_subscription(
            streamer_id=self.streamer_info['id'], streamer_name=self.streamer_info['login'], callbacks=callbacks)

    def execute(self, body=dict):
        options = body['data']['options'][0]['options'][0]

        self.set_streamer_info(options['value'])

        response = self.subscribe_to_online()

        if 'status' in response.keys():
            update_message(body['application_id'], body['token'],
                           f'Failed to subscribe user {options["value"]}. {response["message"]}')

            return

        self.update_dynamo()
        update_message(body['application_id'], body['token'],
                       f'Successfully signed up user {options["value"]}.')

        return
