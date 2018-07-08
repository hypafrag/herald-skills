from plexapi.server import PlexServer
import plexapi.exceptions
import pyatv
import asyncio
import pyatv.interface
import time
import requests.exceptions
import config
import kodi_rpc

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
            print('S{}E{} - {}'.format(season.index, episode.index, episode.title))
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
def _poneys_skill_cr(loop, episode):
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
            client.playMedia(episode)
        except requests.exceptions.RequestException:
            time.sleep(0.5)
            continue
        break

    # yield from atv.logout()
    yield from atv._session.close() # pyatv 0.3.10 has bug in atv.logout method, it doesn't await close()

def _dlna_url(episode):
    try:
        print('Looking for poneys in Kodi library')
        print('Opening {}'.format(config.kodi.tv_shows_source))
        tv_shows_src = kodi_rpc.source('video', config.kodi.tv_shows_source)
        print('Opening {}'.format(episode.grandparentTitle))
        mlp_dir = kodi_rpc.get(tv_shows_src, episode.grandparentTitle)
        print('Opening {}'.format(episode.parentTitle))
        season_dir = kodi_rpc.get(mlp_dir, episode.parentTitle)
        print('Opening {}'.format(episode.title))
        episode_url = kodi_rpc.get(season_dir, episode.index - 1)['file']
    except StopIteration:
        return
    return episode_url

def setup(argparser):
    argparser.description = 'Play poneys'
    argparser.add_argument('where', help='where to play', choices=['main', 'lounge'], default='main', nargs='?')

def use(args):
    episode = _get_poneys()
    if args.where == 'main':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_poneys_skill_cr(loop, episode))
    else:
        kodi_rpc.call('Input.Home', {})
        url = _dlna_url(episode)
        time.sleep(5)
        kodi_rpc.play(url)
