from pathlib import Path

from django import setup
from os import environ
from sys import path as path_sys

BASE_DIR = Path(__file__).resolve().parent.parent
path_sys.append(str(BASE_DIR)+'/')

environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
setup()


from config.settings import redis
from cloud.models import ServerRent


import asyncio
import requests


async def get_data_server(server: ServerRent):
    if 'Windows' in server.os.name:
        await asyncio.sleep(700)
    elif server.location.city == 'Dubai':
        await asyncio.sleep(200)
    else:
        await asyncio.sleep(50)
    response = requests.get(
        'https://api.serverspace.us/api/v1/servers',
        headers={
            'content-type': 'application/json',
            'x-api-key': server.token.key
        }
    )
    print(server.pk, response)

    for s in response.json()['servers']:
        if s['name'] == server.slug:
            server.password = s['password']
            server.username = s['login']
            server.ipv4 = s['nics'][0]['ip_address']
            server.slug = s['id']
            server.save()
            break



async def main():
    while True:
        for note in redis.sscan_iter('notification-complete'):
            print(note)
            command = note.split('::')[0]
            value = note.split('::')[1]
            redis.srem('notification-complete', note)
            if command == 'comserverspace':
                server = ServerRent.objects.get(pk=int(value))
                loop.create_task(get_data_server(server))
        await asyncio.sleep(3)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())