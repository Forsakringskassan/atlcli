import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stderr, stdin
from shared import arguments as arg, trace as trace, output, connection
from bitbucket import functions as cmn

DESCR = 'Changes pull request state for each pull request in input.'
EPILOG = 'The state for the user is passed as a parameter. State is changed only for open pull requests. ' \
        'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Output is state followed by input line. '


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script, True, True)
    status_help = 'Pull request status.'
    parser.add_argument('status', choices=['APPROVED', 'UNAPPROVED', 'NEEDS_WORK'], help=status_help)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)
    status = args.status
    user = arg.get_user(parser, args, 'BITBUCKET', env.script)

    def put(project, repo, pr_id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, pr_id, env.script)
        if pr_data is None:
            return None
        if pr_data['state'] != 'OPEN':
            return ['{}{}{}'.format(line, env.sep, pr_data['state'])]
        addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/participants/{}".format(project, repo, pr_id, user)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        body = {
            'status': status,
            'approved': status == 'APPROVED'
        }
        verb = "PUT"
        message = json.dumps(body)
        uuid = trace.trace_request(env.script, verb, addr, body) if env.trace else None
        conn.request(verb, addr, body=message, headers=h)
        response = conn.getresponse()
        data = json.load(response)
        env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
        if response.status == 200:
            return ['{}{}{}'.format(data['status'], env.sep, line)]
        elif response.status == 403:
            message = data['message']
            stderr.write(
                "\033[31m{}: Failed updating pull request: {}\033[0m{}".format(env.script, message, os.linesep))
            return None
        elif response.status == 400:
            message = data['errors'][0]['message']
            stderr.write(
                "\033[31m{}: Failed updating pull request: {}\033[0m{}".format(env.script, message, os.linesep))
            return None
        else:
            output.print_error(env, addr, response, env.script)
            return None

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 3:
                    stderr.write("\033[31m{}: Bad input, expected at least 3 columns: {}\033[0m{}".format(env.script,
                                                                                                          line,
                                                                                                          os.linesep))
                    exit(3)
                pr_id = columns[0]
                repo = columns[3]
                project = columns[4]
                future = executor.submit(put, project, repo, pr_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
