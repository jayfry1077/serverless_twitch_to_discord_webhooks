from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
import os
import requests

logger = Logger(service='twitch-utils')

STAGE = os.environ.get('STAGE', 'dev')
CLIENT_ID = parameters.get_parameter(
    f'/{STAGE}/twitch/client/id', decrypt=True)
CLIENT_SECRET = parameters.get_parameter(
    f'/{STAGE}/twitch/client/secret', decrypt=True)
TWITCH_OAUTH_URL = 'https://id.twitch.tv/oauth2/token'
TWITCH_STREAMER_URL = 'https://api.twitch.tv/helix/streams'
STREAMER_INFO_URL = 'https://api.twitch.tv/helix/users'


def get_bearer_token():
    params = {'client_id': CLIENT_ID,
              'client_secret': CLIENT_SECRET,
              'grant_type': 'client_credentials'}

    res = requests.post(TWITCH_OAUTH_URL, params=params)

    return res.json()['access_token']


def get_live_stream_info(stremer_id):

    params = {'user_id': stremer_id}
    headers = {'Client-ID': CLIENT_ID,
               'Authorization': f'Bearer {get_bearer_token()}'}

    res = requests.get(TWITCH_STREAMER_URL, params=params,
                       headers=headers).json()

    logger.info(res)

    return res['data']


def get_streamer_info(streamer_login=str):

    params = {'login': streamer_login}
    headers = {'Client-ID': CLIENT_ID,
               'Authorization': f'Bearer {get_bearer_token()}'}

    res = requests.get(STREAMER_INFO_URL,
                       params=params, headers=headers).json()

    return res['data'][0]['profile_image_url']
