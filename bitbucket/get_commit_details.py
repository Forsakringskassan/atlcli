import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, conversion as conversion, output, connection

DESCR = 'Adds commit details for each commit id in input.'
EPILOG = 'Input is commit id (first column), repo (third column) and project (fourth column). ' \
        'Output is input line and added commit information in form of json.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def get_commit_details(project, repo, id, line):
        addr = "/rest/api/1.0/projects/{}/repos/{}/commits/{}".format(project, repo, id)
        # print(addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            created = conversion.to_time(data['committerTimestamp'])
            details = {
                'created': created,
                'committer': data['committer']['name'],
                'message': data['message']
            }
            return ['{}{}{}'.format(json.dumps(details), env.sep, line)]
        else:
            output.print_error(env, addr, response, env.script)
            return None

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
                commit_id = columns[0]
                repo = columns[2]
                project = columns[3]
                future = executor.submit(get_commit_details, project, repo, commit_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
