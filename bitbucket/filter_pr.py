import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, trace as trace, output, connection
from bitbucket import functions as cmn

DESCR = 'For each pull request in input, filter only those pull requests which ' \
        'can be merged and contains changes.'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Only OPEN ' \
        'pull request are included in output. Pipe output to get-pr-files.py or get-pr-details.py or filter-pr.py or ' \
         'put-pr.py or merge-pr.py or delete-pr.py .'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert results, report pull request which cannot be merged or have no changes.')
    parser.add_argument('-s', '--status', choices=['APPROVED', 'UNAPPROVED', 'NEEDS_WORK'],
                        help='Filter on status. Match if at least one reviewer och participant has set this status. '
                             'If this switch is set no other tests are made, '
                             'invert switch is honored though.')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def filter_pr(project, repo, pr_id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, pr_id, env.script)
        if pr_data is None:
            return None
        if pr_data['state'] != 'OPEN':
            return []
        can_merge = merge_data['canMerge']
        if args.status is not None:
            condition = False
            for reviewer in pr_data['reviewers'] + pr_data['participants']:
                if reviewer['status'] == args.status:
                    condition = True
            if condition:
                if args.invert:
                    return []
                else:
                    return [line]
            else:
                if args.invert:
                    return [line]
                else:
                    return []
        if can_merge:
            addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/diff".format(project, repo, pr_id)
            conn = connection.create(env)
            h = {"User-Agent": env.version,
                 "Content-Type": "application/json",
                 "Accept": "application/json",
                 "Authorization": token_header}
            verb = "GET"
            uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
            conn.request(verb, addr, headers=h)
            response = conn.getresponse()
            if response.status == 200:
                data = json.load(response)
                env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
                return [line] if (not args.invert and len(data['diffs']) != 0) or (
                            args.invert and len(data['diffs']) == 0) else []
            else:
                output.print_error(env, addr, response, env.script)
                return None
        elif args.invert:
            return [line]
        else:
            return []

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 5:
                    stderr.write("\033[31m{}: Bad input, expected at least 5 columns: {}\033[0m{}".format(env.script,
                                                                                                          line,
                                                                                                          os.linesep))
                    exit(3)
                pr_id = columns[0]
                repo = columns[3]
                project = columns[4]
                future = executor.submit(filter_pr, project, repo, pr_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
