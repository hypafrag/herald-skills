import notifications


def setup(argparser):
    argparser.description = 'Send notification'
    argparser.add_argument('message', help='message to send', default='yay', nargs='?')


async def use(args):
    await notifications.notify(args.message, sound='yay.aiff')
