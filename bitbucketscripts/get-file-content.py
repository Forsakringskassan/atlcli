#!python -X utf8

from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from bitbucket.get_file_content import DESCR, EPILOG, configure_parser

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

parser = ArgumentParser(description=DESCR, epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
configure_parser(parser, os.path.basename(sys.argv[0]))
args = parser.parse_args()

args.func(parser, args)


