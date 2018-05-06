import socket, ssl, json, struct
import binascii
import config

_apns_host = 'gateway.sandbox.push.apple.com' if config.notifications.apns_sandbox else 'gateway.push.apple.com'

def notify(message, sound='default', badge=0):
    payload = json.dumps({
        'aps': {
            'alert': message,
            'sound': sound,
            'badge': badge,
        },
    }).encode('utf-8')

    chunk_fmt = '!BH32sH%ds' % len(payload)

    chunks = map(
        lambda push_token:
            struct.pack(chunk_fmt, 0, 32, push_token, len(payload), payload),
        map(binascii.unhexlify, config.notifications.apns_push_tokens)
    )

    ssl_sock = ssl.wrap_socket(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM),
        certfile=config.notifications.apns_cert,
        keyfile=config.notifications.apns_key
    )
    ssl_sock.connect((_apns_host, 2195))
    for chunk in chunks:
        ssl_sock.write(chunk)
    ssl_sock.close()
