from sys import stdin

from shared import arguments as arg, output

DESCR = 'Joins input with a named file.'
EPILOG = 'Output is only those rows having matching column values in both input and join file. All columns ' \
         'from input file and join file are output, the columns from the join file after the columns from input. ' \
         'The join columns are only output once. The columns to join must have the same position in both input and ' \
         'join file'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('join', help='Name of file to join.')
    parser.add_argument('column', nargs="*", type=int,
                        help='Column number to join. Order is not important. '
                             'If not given, all columns in join file are included')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    join = open(args.join)
    join_dict = {}
    join_columns = args.column.copy()
    separator = arg.get_separator(args, 'BITBUCKET')

    def get_key_value(columns_, value_=''):
        k = ''
        for i in range(0, len(columns_)):
            cv = columns_[i].strip()
            if i in join_columns:
                k += ('{}{}'.format('' if k == '' else '|', cv))
            elif value_ is not None:
                value_ += ('{}{}'.format(separator, cv))
        return k, value_

    for line in join:
        columns = line.rstrip().split(separator)
        if len(columns) == 0:
            continue
        if len(join_columns) == 0:
            for i in range(0, len(columns)):
                join_columns.append(i)
        key, value = get_key_value(columns)
        join_dict[key] = value
    output_lines = []
    with open(args.file) if args.file else stdin as input:
        for line in input:
            l = line.rstrip()
            columns = l.split(separator)
            if len(columns) == 0:
                continue
            key, dummy = get_key_value(columns, None)
            if key in join_dict:
                output_line = "{}{}".format(l, join_dict[key])
                output_lines.append(output_line)
    output.write(output_lines)
