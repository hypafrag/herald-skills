import argparse

def skill(name):
    __import__('skills.' + name, fromlist=['']).use()

parser = argparse.ArgumentParser(description='Using Herald skills')
parser.add_argument('skill', help='skill to use', choices=[
    'download_poneys',
    'play_poneys'
])

args = parser.parse_args()
skill(args.skill)
