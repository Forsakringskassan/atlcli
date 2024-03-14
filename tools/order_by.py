from _operator import itemgetter
from sys import stdin

from shared import arguments as arg, output

DESCR = 'Sorts the input on a selected column.'
EPILOG = 'Output contains all input rows.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('column', metavar='COLUMN', type=int, help='Column number to sort by.')
    parser.add_argument('-i', '--invert', action='store_true', help='Sorts output in decreasing order.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    separator = arg.get_separator(args, 'BITBUCKET')
    in_data = []
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            columns = line.rstrip().split(separator)
            if len(columns) == 0:
                continue
            in_data.append(columns)

        out_data = sorted(in_data, key=itemgetter(args.column), reverse=args.invert)

        for tuple in out_data:
            output_line = ''
            for i in range(0, len(tuple)):
                value = tuple[i]
                output_line += ('{}{}'.format('' if i == 0 else separator, value))
            output_lines.append(output_line)
    output.write(output_lines)
