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

def _get_poneys():
    print('Looking for poneys in PLEX library')
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
def _start_plex(atv, fast):
    print('Starting PLEX')
    yield from atv.remote_control.top_menu()
    time.sleep(1 if fast else 3)
    yield from atv.remote_control.down()
    for i in range(0, 4):
        yield from atv.remote_control.left()
    for i in range(0, 10):
        yield from atv.remote_control.up()
    time.sleep(1)
    yield from atv.remote_control.up()
    yield from atv.remote_control.down()
    yield from atv.remote_control.select()

def _get_plex_client():
    print('Trying to connect to PLEX')
    client = None
    for i in range(0, 12):
        try:
            client = plex.client(config.plex.clientName)
            break
        except plexapi.exceptions.NotFound:
            time.sleep(0.5)
    return client

@asyncio.coroutine
def _poneys_skill_cr(loop):
    print('Connecting to Apple TV')
    atv = pyatv.connect_to_apple_tv(apple_tv, loop)
    for i in range(0, 3):
        client = _get_plex_client()
        try:
            if client is not None:
                client.stop()
        except requests.exceptions.ConnectionError:
            client = None
        if client is None:
            yield from _start_plex(atv, i == 1)
            time.sleep(1)
            continue
        try:
            client.playMedia(_get_poneys())
        except requests.exceptions.RequestException:
            time.sleep(0.5)
            continue
        break

    # yield from atv.logout()
    yield from atv._session.close() # pyatv 0.3.10 has bug in atv.logout method, it doesn't await close()

def use():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_poneys_skill_cr(loop))
