import re
from sys import stdin

from shared import arguments as arg, output

DESCR = 'For each input line compares the selected column to a value.'
EPILOG = 'Output is the selected input lines where the column value matches the parameter.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('-i', '--invert', action='store_true',
                        help='If given, matching is inverted.')
    parser.add_argument('column', type=int, help='Column number to compare.')
    parser.add_argument('value', help='Regular expression to compare column value to.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    separator = arg.get_separator(args, 'BITBUCKET')
    compare = re.compile(args.value)
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            l = line.rstrip()
            columns = l.split(separator)
            if len(columns) == 0:
                continue
            value = columns[args.column].strip()
            fullmatch = compare.fullmatch(value)
            if fullmatch and not args.invert:
                output_lines.append(l)
            elif not fullmatch and args.invert:
                output_lines.append(l)
    output.write(output_lines)
