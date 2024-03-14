#!python -X utf8

# https://developer.atlassian.com/server/jira/platform/rest-apis/
# https://docs.atlassian.com/jira-software/REST/7.3.1/#agile/1.0/board-getIssuesForBoard
import sys
from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from jira.get_subtasks import DESCR, EPILOG, configure_parser

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

parser = ArgumentParser(description=DESCR, epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
configure_parser(parser, os.path.basename(sys.argv[0]))
args = parser.parse_args()

args.func(parser, args)


