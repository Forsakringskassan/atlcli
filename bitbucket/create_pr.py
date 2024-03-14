from shared import connection
import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, output

DESCR = 'Creates a pull request for each two branch names in input.'
EPILOG = 'Each line starts with the two branch names, followed by the repo name and then project name. ' \
        'The first branch name is the branch to merge from, and the second is the branch to merge to. ' \
        'Output is the pull request id followed by the input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-r', '--reviewer', help='A pull request reviewer')
    parser.add_argument('title', metavar='TITLE', help='Pull reqeust title')
    parser.add_argument('description', metavar='DESCRIPTION', help='The pull request description')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def create_pullrequest(project, repo, from_branch, to_branch, line):
        result = []
        addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests".format(project, repo)
        conn = connection.create(env)
        reviewer = {'user': {'name': args.reviewer}} if args.reviewer else None
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        body = {
            'title': args.title,
            'description': args.description,
            'state': 'OPEN',
            'open': 'true',
            'closed': 'false',
            'fromRef': {
                'id': from_branch,
                'repository': {
                    'slug': repo,
                    'name': None,
                    'project': {
                        'key': project
                    }
                }
            },
            'toRef': {
                'id': to_branch,
                'repository': {
                    'slug': repo,
                    'name': None,
                    'project': {
                        'key': project
                    }
                }
            },
            'locked': 'false',
            'reviewers': [reviewer]
        }
        # print(json.dumps(body))
        verb = "POST"
        message = json.dumps(body)
        uuid = trace.trace_request(env.script, verb, addr, body) if env.trace else None
        conn.request(verb, addr, body=message, headers=h)
        response = conn.getresponse()
        if response.status == 201:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            result.append('{}{}{}'.format(data['id'], env.sep, line))
        else:
            output.print_error(env, addr, response, env.script)
            return None
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 4:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 4 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                from_branch = columns[0]
                to_branch = columns[1]
                repo = columns[2]
                project = columns[3]
                future = executor.submit(create_pullrequest, project, repo, from_branch, to_branch, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
