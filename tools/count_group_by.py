from sys import stdin

from shared import arguments as arg, output

DESCR = 'For the selected columns, counts the number of lines having the same value.'
EPILOG = 'Output is the selected input columns and the number of times they occurr.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('column', nargs="+", type=int,
                        help='column number to include in computation.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    separator = arg.get_separator(args, 'BITBUCKET')
    dict = {}
    with open(args.file) if args.file else stdin as input:
        output_lines = []
        for line in input:
            columns = line.rstrip().split(separator)
            if len(columns) == 0:
                continue
            line = ''
            for i in range(0, len(args.column)):
                c = args.column[i]
                value = columns[c]
                line += ('{}{}'.format('' if i == 0 else separator, value))
            if line in dict:
                dict[line] += 1
            else:
                dict[line] = 1
        for key in dict:
            output_lines.append("{}{}{}".format(key, separator, dict[key]))
        output.write(output_lines)
