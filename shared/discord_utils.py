import requests
import json


def call_discord(discord_webhook, data):
    res = requests.post(discord_webhook, json={'content': json.dumps(data)}, headers={
                        'Content-type': 'application/json'})
    print('Response ' + res.text)
