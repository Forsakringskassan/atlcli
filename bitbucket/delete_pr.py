import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import connection

from shared import arguments as arg, trace as trace, output
from bitbucket import functions as cmn

DESCR = 'Deletes each pull request in input.'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Output is input line with "DELETED" prepended.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def delete_pr(project, repo, pr_id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, pr_id, env.script)
        if pr_data is None or merge_data is None:
            return None
        version = pr_data['version']
        addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}".format(project, repo, pr_id)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        body = {
            'version': version,
        }
        message = json.dumps(body)
        verb = "DELETE"
        uuid = trace.trace_request(env.script, verb, addr, body) if env.trace else None
        conn.request(verb, addr, body=message, headers=h)
        response = conn.getresponse()
        if response.status == 204:
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status)
            return ["DELETED{}{}".format(env.sep, line)]
        else:
            output.print_error(env, addr, response, env.script)
            return None

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 5:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 5 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                pr_id = columns[0]
                repo = columns[3]
                project = columns[4]
                future = executor.submit(delete_pr, project, repo, pr_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
