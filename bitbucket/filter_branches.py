import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, output
from bitbucket import functions as cmn

DESCR = 'For each branch in input, filters existing branches.'
EPILOG = 'Input is a number of branch names followed by repo (next last column) and project (last column). ' \
         'Only input lines where all branches exist are included in ' \
         'output. Pipe output to get-commits.py or delete-branches.py or filter-merged.py or ' \
         'get-file-names.py or create-pr.py or get-pr.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')

    def filter_branch(project, repo, names, line):
        result = []
        matches = cmn.get_branch_or_tag(env, project, repo, 'branches', names, env.script)
        if None not in matches:
            result.append(line)
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                length = len(columns)
                if length < 3:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 3 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                project = columns[length - 1]
                repo = columns[length - 2]
                names = columns[:length - 3]
                future = executor.submit(filter_branch, project, repo, names, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
