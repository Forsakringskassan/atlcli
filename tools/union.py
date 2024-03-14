from sys import stdin

from shared import arguments as arg, output

DESCR = 'Unions input with a named file.'
EPILOG = 'Output is all lines from input appended with new lines from the unioned file.'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('union', help='Name of file to join.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    union = open(args.union)
    union_dict = {}
    separator = arg.get_separator(args, 'BITBUCKET')

    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            strip_line = line.rstrip()
            columns = strip_line.split(separator)
            if len(columns) == 0:
                continue
            union_dict[strip_line] = strip_line
            output_lines.append(strip_line)
    for line in union:
        union_strip_line = line.rstrip()
        columns = union_strip_line.split(separator)
        if len(columns) == 0:
            continue

        if union_strip_line not in union_dict:
            output_lines.append(union_strip_line)
    output.write(output_lines)
