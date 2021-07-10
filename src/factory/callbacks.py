class CallbackFactory:
    def serialize(self, data):
        seralizer = get_serializer(data)
        return seralizer(data)


def get_serializer(data):
    if data['callback']['platform'] == 'discord':
        return _serialize_to_discord

    elif data['callback']['platform'] == 'guilded':
        return _serialize_to_guilded

    else:
        return ValueError(data['callback']['platform'])


def _serialize_to_discord(data):

    name = data['broadcaster_name']
    game = data['live_stream_info'][0]['game_name']
    title = data['live_stream_info'][0]['title']
    message = data['callback']['message'].format(
        message=f"{name} is live - {game}\n{title}\nhttps://www.twitch.tv/{data['broadcaster_url_id']}")

    return {'content': message}


def _serialize_to_guilded(data=dict) -> dict:

    body = {
        'title': f"{data['broadcaster_name']} is live - {data['live_stream_info'][0]['game_name']}",
        'url': f"https://www.twitch.tv/{data['broadcaster_url_id']}",
        'image': {
            'url': data['profile_image_url']
        },
        'description': data['live_stream_info'][0]['title']
    }

    return {'embeds': [body]}
