import os
import re
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, output
from bitbucket import functions as cmn

DESCR = 'For each repo in input, lists or searches branch and tag names.'
EPILOG = 'Input is repo (first column) and project (second column). Other columns are ignored. ' \
         'Branch fully qualified names are used in the output, ' \
        'unless switch -d is used. ' \
        'If switch -n is defined only those repos with all matching names are included in output. ' \
        'Each output line consists of all matching branches and tags, in separate columns, followed by input line. ' \
        'If there are multiple names matching a pattern, '\
        'the largest name is used. ' \
        'Name comparison is semantic version aware. The names are split using full stop, and each part ' \
        'is compared. A longer string is "larger" than a short string in a versionized name. If there are no ' \
        'full stops in the name, traditional string comparison is used. ' \
        'If switch -n is not defined, all branches and tags are included in output, each on a separate line. ' \
         'Pipe output to get-commits.py or delete-branches.py or filter-branches.py or filter-merged.py or ' \
         'get-file-names.py or create-pr.py or get-pr.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    branches_help = 'Space separated list of regular expressions defining branch or tag names. ' \
                    'The display name us used here as it ' \
                    'is shorter. If no name is given all branches and tags are returned, each on a separate line.'
    parser.add_argument('-n', '--names', nargs='+', help=branches_help)
    parser.add_argument('-d', '--displayid', action='store_true',
                        help='Output displayid instead of id, useful for bash integration')
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert logic. Only repos with all listed names missing are included in output. '
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
                    stderr.write(f"\033[31m{env.script}: Bad input, "
                                 f"expected at least 2 columns: {line}\033[0m{os.linesep}")
                    exit(3)
                repo = columns[0]
                project = columns[1]
                future = executor.submit(cmn.search_branch_or_tag, env, project, repo, rstrip, 'branchestags', patterns,
                                         None, args.displayid, args.invert, env.script)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
    parser.set_defaults(func=main)

