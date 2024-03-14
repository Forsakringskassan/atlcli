import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, trace as trace, output, connection
from bitbucket import functions as cmn

DESCR = 'Merge each pull request in input if possible'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Output is input and the new state prepended. If the pull request cannot be ' \
        'merged this is reported as CANNOT-MERGE.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('message', metavar='MESSAGE', help='Merge commit message.')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def merge(project, repo, pr_id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, pr_id, env.script)
        if pr_data is None:
            return None
        if pr_data['state'] != 'OPEN':
            return ['{}{}{}'.format(line, env.sep, pr_data['state'])]
        version = pr_data['version']
        canmerge = merge_data['canMerge']
        if canmerge:
            addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/merge".format(project, repo, pr_id)
            conn = connection.create(env)
            h = {"User-Agent": env.version,
                 "Content-Type": "application/json",
                 "Accept": "application/json",
                 "Authorization": token_header}
            body = {
                'version': version,
                'message': args.message
            }
            verb = "POST"
            message = json.dumps(body)
            uuid = trace.trace_request(env.script, verb, addr, message) if env.trace else None
            conn.request(verb, addr, body=message, headers=h)
            response = conn.getresponse()
            if response.status == 200:
                data = json.load(response)
                env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
                return ['{}{}{}'.format(data['state'], env.sep, line)]
            else:
                output.print_error(env, addr, response, env.script)
                return None

        else:
            return ['CANNOT-MERGE{}{}'.format(env.sep, line)]

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
                future = executor.submit(merge, project, repo, pr_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
