import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, trace as trace, output, connection

DESCR = 'For each repo in input adds the clone url.'
EPILOG = 'Input is repo name followed project name. Output is the clone url followed by input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-e', '--type',
                        default='ssh',
                        choices=['ssh', 'http'],
                        help='Type of url to get')
    parser.set_defaults(func=main)

def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def get_repo_urls(project, repo, line, type):
        result = []
        addr = "/rest/api/1.0/projects/{}/repos/{}".format(project, repo)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            hrefs = data['links']['clone']
            for item in hrefs:
                if item['name'] == type:
                    result.append("{}{}{}".format(item['href'], env.sep, line))
                    break
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
                if len(columns) < 2:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 2 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                repo = columns[0]
                project = columns[1]
                future = executor.submit(get_repo_urls, project, repo, rstrip, args.type)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
