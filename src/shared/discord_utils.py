from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
import json

logger = Logger(service='discord-utils')
STAGE = os.environ.get('STAGE', 'dev')
DISCORD_PUBLIC_KEY = parameters.get_parameter(
    f'/{STAGE}/discord/public/key', decrypt=True)


def valid_signature(event):
    body = event['body']
    auth_sig = event['headers']['x-signature-ed25519']
    auth_ts = event['headers']['x-signature-timestamp']

    message = auth_ts.encode() + body.encode()

    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(message, bytes.fromhex(auth_sig))

        return True
    except BadSignatureError as e:
        print(e)
        return False
