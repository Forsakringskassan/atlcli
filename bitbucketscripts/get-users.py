#!python.exe -X utf8

# https://developer.atlassian.com/server/bitbucket/rest/v806/api-group-system-maintenance/#api-api-latest-users-get
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp366

from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bitbucket.get_users import DESCR, EPILOG, configure_parser, main

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

parser = ArgumentParser(description=DESCR, epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
configure_parser(parser, os.path.basename(sys.argv[0]))
args = parser.parse_args()

args.func(parser, args)
