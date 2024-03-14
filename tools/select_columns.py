from sys import stdin

from shared import arguments as arg, output

DESCR = 'For each input line outputs the selected columns.'
EPILOG = 'Output is the selected input columns in the order defined by the arguments.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('column', nargs="+", type=int,
                        help='column number to include in output.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    separator = arg.get_separator(args, 'BITBUCKET')
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            columns = line.rstrip().split(separator)
            if len(columns) == 0:
                continue
            result = ''
            for i in range(0, len(args.column)):
                c = args.column[i]
                value = columns[c]
                result += ('{}{}'.format('' if i == 0 else separator, value))
            output_lines.append(result)
    output.write(output_lines)
