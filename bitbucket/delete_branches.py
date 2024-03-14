import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, trace as trace, output, connection

DESCR = 'Deletes a branch foreach branch name in input.'
EPILOG = 'Input is branch name, repo and project. Output is "DELETED" followed by input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')

    def delete_branch(project, repo, branch, line):
        token_header = "Bearer {}".format(env.token)
        result = []
        addr = "/rest/branch-utils/1.0/projects/{}/repos/{}/branches".format(project, repo)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        body = {
            'name': branch,
            'dryRun': 'false'
        }
        # print(json.dumps(body))
        verb = "DELETE"
        uuid = trace.trace_request(env.script, verb, addr, body) if env.trace else None
        conn.request(verb, addr, body=json.dumps(body), headers=h)
        response = conn.getresponse()
        if response.status == 204:
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status)
            result.append("DELETED{}{}".format(env.sep, line))
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
                if len(columns) < 3:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 3 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                branch = columns[0]
                repo = columns[1]
                project = columns[2]
                future = executor.submit(delete_branch, project, repo, branch, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
