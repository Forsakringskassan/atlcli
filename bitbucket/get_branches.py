import os
import re
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, output
from bitbucket import functions as cmn

DESCR = 'For each repo in input, lists or searches branch names.'
EPILOG = 'Input is repo (first column) and project (second column). Other columns are ignored. Branch fully qualified names are used in the output, ' \
        'unless switch -d is used. ' \
        'If switch -n is defined only those repos with all matching branches are included in output. ' \
        'Each output line consists of all matching branches, in separate columns, followed by input line. ' \
        'If there are multiple branches matching a branch pattern, '\
        'the largest branch name is used. This can be handy to find current release branch for example. ' \
        'Branch name comparison is semantic version aware. The branch names are split using full stop, and each part ' \
        'is compared. A longer string is "larger" than a short string in a versionized name. If there are no ' \
        'full stops in the name, traditional string comparison is used. ' \
        'If switch -n is not defined, all branches are included in output, each branch on a separate line. ' \
         'Pipe output to get-commits.py or delete-branches.py or filter-branches.py or filter-merged.py or ' \
         'get-file-names.py or create-pr.py or get-pr.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    branches_help = 'Space separated list of regular expressions defining branches. The display name us used here as it ' \
                    'is shorter. If no branch name is given all branches are returned, each on a separate line.'
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--names', nargs='+', help=branches_help)
    group.add_argument('-f', '--default', action='store_true',
                       help='Output default branch. Cannot be used with -n switch.')
    parser.add_argument('-d', '--displayid', action='store_true',
                        help='Output displayid instead of id, useful for bash integration')
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert logic. Only repos with all listed branches missing are included in output. '
                             'Only makes sense with -n switch')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    patterns = []
    if args.names is not None:
        for b in args.names:
            pattern = re.compile(b)
            patterns.append(pattern)
    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 2:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 2 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                repo = columns[0]
                project = columns[1]
                future = executor.submit(cmn.search_branch_or_tag, env, project, repo, rstrip, 'branches', patterns,
                                         args.default, args.displayid, args.invert, env.script)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
