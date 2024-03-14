import os
import sys
from sys import stdout, version_info

from shared import arguments as arg

DESCR = 'Prints version info'
EPILOG = 'Different version info is printed to stout.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', os.path.basename(sys.argv[0]), False)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    stdout.write("version:{}{}".format(env.version, os.linesep))
    stdout.write("version_info:{}{}".format(version_info, os.linesep))
