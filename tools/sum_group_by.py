from string import Template
from sys import stdin

from shared import arguments as arg, output


class NumTemplate(Template):
    idpattern = "[0-9]+"


DESCR = 'Sums column values having matching values in other columns '
EPILOG = 'Output is bla bla bal'


def configure_parser(parser, script):
    parser.add_argument('-l', '--file',
                        help='If given, input is read from this file. Otherwise input is read from stdin.')
    parser.add_argument('function',
                        help='function to execute for each input line. Give a python expression naming the columns'
                             'using string templates naming the column number. Using column three: "${3}". '
                             'Adding colums 2 and three: \'${2} + ${3}\'. Beware of bash substitution ')
    parser.add_argument('group', nargs="+", type=int,
                        help='Column numbers to group by.')
    arg.add_separator(parser, 'BITBUCKET')
    parser.set_defaults(func=main)


def main(parser, args):
    group_columns = args.group.copy()
    separator = arg.get_separator(args, 'BITBUCKET')
    function = NumTemplate(args.function)
    output_lines = []
    groups_result = {}
    groups_input = {}
    with open(args.file) if args.file else stdin as input:
        for line in input:
            l = line.rstrip()
            columns = l.split(separator)
            if len(columns) == 0:
                continue
            hash = {}
            for i in range(0, len(columns)):
                key = str(i)
                hash[key] = columns[i]
            expr = function.substitute(hash)
            result = eval(expr)

            group = ""
            for i in group_columns:
                group = "{}|{}".format(group, columns[i])
            if group not in groups_input.keys():
                output_columns = []
                for i in group_columns:
                    output_columns.append(columns[i])
                groups_input[group] = output_columns
                groups_result[group] = result
            else:
                groups_result[group] = groups_result[group] + result
    for key in groups_input.keys():
        input_line = groups_input[key]
        line = input_line[0]
        for i in range(1, len(input_line)):
            line = "{}{}{}".format(line, separator, line[i])
        line = "{}{}{}".format(line, separator, groups_result[key])
        output_lines.append(line)
    output.write(output_lines)
