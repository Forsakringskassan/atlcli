import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, output, connection

DESCR = 'For each project in input, lists all repos.'
EPILOG = \
    'Input is each project name on a separate line. Output is repo name followed by project name, separated by tab. ' \
    'Pipe output to get-branches.py or get-tags.py or get-branchesor-tags.py or get-clone-urls.py or get-pr.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    state_help = 'Repository state.'
    STATE_CHOICES = ['AVAILABLE', 'INITIALISING', 'INITIALISATION_FAILED']
    parser.add_argument('-s', '--state', default='AVAILABLE', choices=STATE_CHOICES, help=state_help)
    parser.add_argument('-c', '--count', action='store_true', help='Output number of repos instead of names')
    parser.set_defaults(func=main)

    
def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def get_project_repos(project, line):
        result = []
        page = 0
        is_last_page = False
        count = 0
        while not is_last_page:
            addr = "/rest/api/1.0/projects/{}/repos?start={}".format(project, page)
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
                for value in data['values']:
                    if value['state'] == args.state:
                        if args.count:
                            count += 1
                        else:
                            result.append("{}{}{}".format(value['slug'], env.sep, line))
                is_last_page = data['isLastPage']
                if not is_last_page:
                    page = data['nextPageStart']
            else:
                output.print_error(env, addr, response, env.script)
                return None

        if args.count:
            result.append("{}{}{}".format(count, env.sep, line))
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 1:
                    stderr.write(f"\033[31m{env.script}: Bad input, input is only whitespace\033[0m{os.linesep}")
                    exit(3)
                project = columns[0]
                future = executor.submit(get_project_repos, project, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
