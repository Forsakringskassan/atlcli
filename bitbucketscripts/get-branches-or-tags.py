#!python -X utf8

# https://developer.atlassian.com/server/bitbucket/reference/rest-api/
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp181
# https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp181

import os
import sys
from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bitbucket.get_branches_or_tags import DESCR, EPILOG, configure_parser

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

main_parser = ArgumentParser(description=DESCR, epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
configure_parser(main_parser, os.path.basename(sys.argv[0]))
args = main_parser.parse_args()

args.func(main_parser, args)
