import ssl, json, struct
import binascii
import asyncio
import os
import base64
from db import redis

_apns_host = 'gateway.sandbox.push.apple.com' if False else 'gateway.push.apple.com'

_CERT = base64.decodebytes(bytes(os.environ['HS_APS_CERT'], encoding='UTF-8'))
_PKEY = base64.decodebytes(bytes(os.environ['HS_APS_PKEY'], encoding='UTF-8'))

with open('/tmp/hs_aps_cert.pem', 'wb') as f:
    f.write(_CERT)

with open('/tmp/hs_aps_pkey.pem', 'wb') as f:
    f.write(_PKEY)


async def notify(message, sound='default', badge=0):
    payload = json.dumps({
        'aps': {
            'alert': message,
            'sound': sound,
            'badge': badge,
        },
    }).encode('utf-8')

    chunk_fmt = '>BIBH32sBH%dsBHI' % len(payload)
    frame_len = struct.calcsize(chunk_fmt) - 5

    _, herald_push_tokens = redis.sscan('herald_push_tokens')
    chunks = map(
        lambda index__push_token:
            struct.pack(chunk_fmt,
                        2,
                        frame_len,
                        1, 32, binascii.unhexlify(index__push_token[1]),
                        2, len(payload), payload,
                        3, 4, index__push_token[0]),
        enumerate(herald_push_tokens))

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_cert_chain('/tmp/hs_aps_cert.pem', '/tmp/hs_aps_pkey.pem')

    async def connect():
        return await asyncio.open_connection(host=_apns_host, port=2195, ssl=ssl_context)
    r, w = None, None

    for chunk in chunks:
        if w is None:
            r, w = await connect()
        w.write(chunk)
        await w.drain()
        try:
            response = await asyncio.wait_for(r.read(6), 1)
            cmd, status, index = struct.unpack('>BBI', response)
            if status == 8:
                print('Delete', herald_push_tokens[index])
                redis.srem('herald_push_tokens', herald_push_tokens[index])
            w.close()
            r, w = None, None
        except asyncio.TimeoutError:
            pass

    if w is not None:
        w.close()
