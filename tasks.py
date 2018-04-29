from plexapi.server import PlexServer
import plexapi.exceptions
import pyatv
import asyncio
import pyatv.interface
import time
import requests.exceptions
import config

plex = PlexServer('http://{}:{}'.format(config.plex.host, config.plex.port), config.plex.onlineToken)
apple_tv = pyatv.AppleTVDevice(config.apple_tv.name, config.apple_tv.host, config.apple_tv.loginId)

def get_poneys():
    tv_shows = plex.library.section('TV Shows')
    mlp = tv_shows.get('My Little Pony: Friendship is Magic')
    for season in mlp:
        if season.isWatched:
            continue
        for episode in season:
            if episode.isWatched:
                continue
            # print('S{}E{} - {}'.format(season.index, episode.index, episode.title))
            return episode

@asyncio.coroutine
def start_plex(atv):
    yield from atv.remote_control.top_menu()
    time.sleep(1)
    yield from atv.remote_control.down()
    for i in range(0, 4):
        yield from atv.remote_control.left()
    for i in range(0, 10):
        yield from atv.remote_control.up()
    time.sleep(1)
    yield from atv.remote_control.up()
    yield from atv.remote_control.down()
    yield from atv.remote_control.select()

def get_plex_client():
    client = None
    for i in range(0, 12):
        try:
            client = plex.client(config.plex.clientName)
            break
        except plexapi.exceptions.NotFound:
            time.sleep(0.5)
    return client

@asyncio.coroutine
def run_application(loop):
    atv = pyatv.connect_to_apple_tv(apple_tv, loop)
    for i in range(0, 3):
        client = get_plex_client()
        if client is None:
            yield from start_plex(atv)
            continue
        try:
            client.playMedia(get_poneys())
        except requests.exceptions.RequestException:
            yield from start_plex(atv)
            continue
        break
    yield from atv.logout()

def poneys_skill():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_application(loop))

poneys_skill()
