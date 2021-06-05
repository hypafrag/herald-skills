from plexapi.server import PlexServer
import plexapi.exceptions
import time
import requests.exceptions
import kodi_rpc
import os

plex = PlexServer('http://{}:{}'.format(os.environ['HS_PLEX_HOST'],
                                        os.environ['HS_PLEX_PORT']),
                  os.environ['HS_PLEX_ONLINE_TOKEN'])


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


def _get_plex_client():
    print('Trying to connect to PLEX')
    client = None
    for i in range(0, 12):
        try:
            client = plex.client(os.environ['HS_PLEX_PLAYER_NAME'])
            break
        except plexapi.exceptions.NotFound:
            time.sleep(0.5)
    return client


async def _poneys_skill(episode):
    for i in range(0, 3):
        client = _get_plex_client()
        try:
            if client is not None:
                client.stop()
        except requests.exceptions.ConnectionError:
            client = None
        try:
            client.playMedia(episode)
        except requests.exceptions.RequestException:
            time.sleep(0.5)
            continue
        break


def _dlna_url(episode):
    try:
        print('Looking for poneys in Kodi library')
        tv_shows_src = kodi_rpc.source('video', 'TV Shows')
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


async def use(args):
    episode = _get_poneys()
    if args.where == 'main':
        await _poneys_skill(episode)
    else:
        kodi_rpc.call('Input.Home', {})
        url = _dlna_url(episode)
        time.sleep(5)
        kodi_rpc.play(url)
