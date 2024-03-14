#!python -X utf8

# https://developer.atlassian.com/server/bitbucket/reference/rest-api/
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp260
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp258
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp266

import sys
from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bitbucket.delete_pr import DESCR, EPILOG, configure_parser

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

parser = ArgumentParser(description=DESCR, epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
configure_parser(parser, os.path.basename(sys.argv[0]))
args = parser.parse_args()

args.func(parser, args)
