import argparse
import sys

def skill(name, argv):
    skill = __import__('skills.' + name, fromlist=[''])
    argparser = argparse.ArgumentParser(name)
    skill.setup(argparser)
    args = argparser.parse_args(argv)
    skill.use(args)

argparser = argparse.ArgumentParser(description='Using Herald skills')
argparser.add_argument('skill', help='skill to use', choices=[
    'download_poneys',
    'play_poneys'
])

args = argparser.parse_args(sys.argv[1:2])
skill(args.skill, sys.argv[2:])
