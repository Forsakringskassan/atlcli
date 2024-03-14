from shared import version

DESCR = 'Compares version numbers.'
EPILOG = 'Output is a 1 if second version is higher than first version. 0 if they are equal. -1 if first version is less than the second.'


def configure_parser(parser, script):
    parser.add_argument('-b', '--binary',
                        help='If given result is returned to shell as well as text output.')
    parser.add_argument('first', metavar='FIRST', help='First version to compare.')
    parser.add_argument('second', metavar='SECOND', help='Second version to compare.')
    parser.set_defaults(func=main)


def main(parser, args):
    first_str = args.first
    second_str = args.second
    first_v = version.Version(first_str)
    second_v = version.Version(second_str)
    # print(first_v)
    # print(second_v)
    result = -2
    if first_v == second_v:
        result = 0
    elif second_v > first_v:
        result = 1
    else:
        result = -1
    print(result)
    if args.binary:
        exit(result)
