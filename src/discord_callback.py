from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from factory.discord_commands import get_executor
import os
import json


logger = Logger(service='discord-callback')
STAGE = os.environ.get('STAGE', 'dev')
DISCORD_PING_PONG = {'statusCode': 200, "headers": {
    "content-type": 'application/json'}, 'body': json.dumps({"type": 1})}
ALLOWED_ROLES = parameters.get_parameter(
    f'/{STAGE}/discord/allowed/roles', decrypt=True)


def discord_body(status_code=int, type=int, message=str):
    return {
        "statusCode": status_code,
        "headers": {"content-type": 'application/json'},
        'body': json.dumps({"type": type,
                            "data": {
                                "tts": False,
                                "content": message}})
    }


def main(event, context):
    print(event)

    body = event['detail']

    incoming_roles = body['member']['roles']
    allowed_roles = [role for role in ALLOWED_ROLES.split(',')]
    allowed = False

    for role in allowed_roles:
        if role in incoming_roles:
            allowed = True

    if not allowed:
        return discord_body(200, 4, 'You are not allowed to do this!')

    command = body['data']['options'][0]['name']

    try:
        executor = get_executor(command)
        executor.execute(body)
        return
    except Exception as e:
        logger.error(e)
        return discord_body(200, 4, 'Something went wrong')
