import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, output
from bitbucket import functions as cmn

DESCR = 'Creates a new branch for each commit id in input.'
EPILOG = 'Input line is commit id (first column), repo name (third column) and project name (fourth column). ' \
        'Output is the new branch name followed by repo name and the project name'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('name', metavar='NAME',
                        help='The display name of the new branches')
    message_help = 'Message for branch.'
    parser.add_argument('-m', '--message', default='Created by create-branches', help=message_help)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    name = args.name
    message = args.message
    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                columns = line.rstrip().split(env.sep)
                if len(columns) < 4:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 4 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                commit = columns[0]
                repo = columns[2]
                project = columns[3]
                future = executor.submit(cmn.create_branch_or_tag, env, project, repo, 'branches', commit,
                                         name, message, env.script)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
