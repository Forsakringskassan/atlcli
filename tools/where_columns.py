from sys import stdin

from shared import arguments as arg, output

DESCR = 'For each input line compares two columns.'
EPILOG = 'Output is the input lines where the column values matches the condition.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('first', type=int, help='First column number to compare.')
    parser.add_argument('condition', help='Condition for comparison.')
    parser.add_argument('second', type=int, help='Second column to compare.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    separator = arg.get_separator(args, 'BITBUCKET')
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            l = line.rstrip()
            columns = l.split(separator)
            if len(columns) == 0:
                continue
            first = columns[args.first].strip()
            condition = args.condition
            second = columns[args.second].strip()
            expression = f"{first} {condition} {second}"
            evaluation = eval(expression)
            if evaluation:
                output_lines.append(l)
    output.write(output_lines)
