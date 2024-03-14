from sys import stdin

from shared import arguments as arg, output

DESCR = 'Remove rows from input matching rows in named file.'
EPILOG = 'Output is only those rows in input not having matching column values in named file. '


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('minus', help='Name of file to minus.')
    parser.add_argument('column', nargs="*", type=int,
                        help='Column number to minus. Order of arguments are not important. '
                             'If not given, all columns in minus file are included')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    minus = open(args.minus)
    minus_dict = {}
    minus_columns = args.column.copy()
    separator = arg.get_separator(args, 'BITBUCKET')

    def get_key_value(columns_, value_=''):
        k = ''
        for i in range(0, len(columns_)):
            cv = columns_[i].strip()
            if i in minus_columns:
                k += ('{}{}'.format('' if k == '' else '|', cv))
            elif value_ is not None:
                value_ += ('{}{}'.format(separator, cv))
        return k, value_

    for line in minus:
        columns = line.rstrip().split(separator)
        if len(columns) == 0:
            continue
        if len(minus_columns) == 0:
            for i in range(0, len(columns)):
                minus_columns.append(i)
        key, value = get_key_value(columns)
        minus_dict[key] = value
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            l = line.rstrip()
            columns = l.split(separator)
            if len(columns) == 0:
                continue
            key, dummy = get_key_value(columns, None)
            if key not in minus_dict:
                output_lines.append(l)
    output.write(output_lines)
