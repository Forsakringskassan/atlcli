import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, output
from bitbucket import functions as cmn

DESCR = 'For each branch in input, prints latest commit id.'
EPILOG = 'Input is branch (first column), repo (second column) and project (third column). ' \
        'Output is commit id followed by input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):

    def get_commits(project, repo, name, line):
        branch_or_tag = 'tags' if 'tags' in name else 'branches'
        values = cmn.get_branch_or_tag(env, project, repo, branch_or_tag, [name], env.script)
        commit = values[0]['latestCommit']
        return "{}{}{}".format(commit, env.sep, line)

    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    # token_header = "Bearer {}".format(env.token)
    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 3:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 2 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                name = columns[0]
                repo = columns[1]
                project = columns[2]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_commits, project, repo, name, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
