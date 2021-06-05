import requests
import json


def call(method, params):
    pass
    # return requests.post('http://{}:{}/jsonrpc'.format(config.kodi.host, config.kodi.port), data=json.dumps({
    #     'method': method,
    #     'params': params,
    #     'jsonrpc': '2.0',
    #     'id': 1,
    # }), headers={'content-type': 'application/json'}).json()


def source(type, name):
    return next(filter(lambda source: source['label'] == name,
                       call('Files.GetSources', {'media': type})['result']['sources']))


def get(parent, item):
    files = call('Files.GetDirectory', {'directory': parent['file']})['result']['files']
    if isinstance(item, int):
        return files[item]
    else:
        return next(filter(lambda entry: entry['label'] == item, files))


def play(item):
    call('Player.Open', {'item': {'file': item}})

# http://192.168.1.23:8080/jsonrpc?request={"jsonrpc":"2.0","id":1,"method":"Addons.ExecuteAddon" ,"params":{"addonid":"script.plex","params":{}}}