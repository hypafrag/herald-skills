from plexapi.server import PlexServer
from html.parser import HTMLParser
import urllib.request
import urllib.error
import shutil
import re
import requests
import notifications
import os

plex = PlexServer('http://{}:{}'.format(os.environ['HS_PLEX_HOST'], os.environ['HS_PLEX_PORT']), os.environ['HS_PLEX_ONLINE_TOKEN'])

poneys_dir = os.environ['HS_PONEYS_DIR']


class _YPParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._junk = False
        self._hrefs = {}
        self._link_regex = re.compile(r'^http.*(\d\dx\d\d).*\.mkv$')

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if self._junk:
            return
        if tag == 'div' and ('id', 'junk') in attrs:
            self._junk = True
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    match = self._link_regex.findall(attr[1])
                    if match:
                        self._hrefs[match[0]] = attr[1]

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

    def links(self):
        return self._hrefs


def _season_episode_links(i):
    parser = _YPParser()
    url = 'https://yp1.yayponies.no/videos/tables/1i{}.html'.format(i)
    try:
        parser.feed(urllib.request.urlopen(url).read().decode('utf-8'))
    except urllib.error.HTTPError:
        return {}

    return parser.links()


def _get_link(s, e):
    s_links = _season_episode_links(s)
    key = '{:0>2}x{:0>2}'.format(s, e)
    if key in s_links:
        return s_links[key], s, e
    return None, None, None


def _download(link, s, e):
    stat_info = os.stat(poneys_dir)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    tmp_file = '/tmp/MLP{:0>2}x{:0>2}.mkv'.format(s, e)
    file = '{}/My Little Pony: Friendship Is Magick {:0>2}x{:0>2}.mkv'.format(poneys_dir, s, e)

    r = requests.get(link, stream=True)
    print('Downloading', link)
    if r.status_code == 200:
        with open(tmp_file, 'wb') as f:
            r.raw.decode_content = True
            file_size = int(r.headers.get('Content-Length'))
            chunk_size = 64 * 1024
            read_size = 0
            while True:
                buf = r.raw.read(chunk_size)
                if not buf:
                    break
                read_size += len(buf)
                # print('{}'.format(read_size / file_size))
                f.write(buf)

    os.chown(tmp_file, uid, gid)
    shutil.move(tmp_file, file)


def setup(argparser):
    pass


async def use(args):
    tv_shows = plex.library.section('TV Shows')
    mlp = tv_shows.get('My Little Pony: Friendship is Magic')

    last_season = None
    for last_season in mlp.seasons():
        pass

    last_episode = None
    for last_episode in last_season.episodes():
        pass

    link, s, e = _get_link(last_season.index, last_episode.index + 1)
    if link is None:
        link, s, e = _get_link(last_season.index + 1, 1)
    if link is not None:
        await notifications.notify('Started downloading poneys S{:0>2}E{:0>2}'.format(s, e), sound='yay.aiff')
        _download(link, s, e)
        await notifications.notify('Downloaded poneys S{:0>2}E{:0>2}'.format(s, e), sound='yay.aiff')
        tv_shows.update()
    else:
        print('Latest is S{}E{}'.format(last_season.index, last_episode.index))
