import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, output, trace as trace, connection

DESCR = 'Prints pull request id for each input line. '
EPILOG = 'Input starts with two optional branch names, followed by repo and project name. ' \
         'If two branch names are given, the first branch name is the outgoing branch and the ' \
         'second is the incoming branch. ' \
         'If only project and repo names are defined in input, all pull requests are listed. ' \
         'If one branch is defined in input, output depends on --direction switch. ' \
         'Output is pull request id followed by outgoing branch, incoming branch, repo and project. ' \
         'Pipe output to get-pr-files.py or get-pr-details.py or filter-pr.py or put-pr.py or ' \
         'merge-pr.py or delete-pr.py .'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    state_help = 'Pull request state.'
    parser.add_argument('-s', '--state', default='OPEN', choices=['OPEN', 'DECLINED', 'MERGED', 'ALL'], help=state_help)
    direction_help = 'Branch direction if only one branch in input. IN means branch name is incoming. OUT means branch ' \
                     'name is outgoing. EITHER means branch name is matched to both incoming and outgoing branches.'
    parser.add_argument('-d', '--direction', default='EITHER', choices=['OUT', 'IN', 'EITHER'], help=direction_help)
    parser.set_defaults(func=main)

def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def get_pr(project, repo, outgoing, incoming, either):
        output.print_debug(env, "project={}, repo={}, outgoing={}, incoming={}, either={}"
                           .format(project, repo, outgoing, incoming, either))
        result = []
        page = 0
        is_last_page = False
        while not is_last_page:
            addr = \
                "/rest/api/1.0/projects/{}/repos/{}/pull-requests?state={}&start={}".format(project, repo, args.state,
                                                                                            page)
            output.print_debug(env, "addr={}".format(addr))
            conn = connection.create(env)
            h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
            verb = "GET"
            uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
            conn.request(verb, addr, headers=h)
            response = conn.getresponse()
            if response.status == 200:
                data = json.load(response)
                output.print_debug(env, json.dumps(data))
                env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
                for value in data['values']:
                    from_ref = value['fromRef']['id']
                    to_ref = value['toRef']['id']
                    pr_id = value['id']
                    if (either is None and outgoing is None and incoming is None) or \
                            (either is not None and (from_ref == either or to_ref == either) or
                             (either is None and
                              (outgoing is None or from_ref == outgoing) and (incoming is None or to_ref == incoming))):
                        result.append('{}{}{}{}{}{}{}{}{}'.
                                      format(pr_id, env.sep, from_ref, env.sep, to_ref, env.sep, repo, env.sep,
                                             project))
                is_last_page = is_last_page or data['isLastPage']
                if not is_last_page:
                    page = data['nextPageStart']
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
                if len(columns) == 3:
                    either = columns[0] if args.direction == 'EITHER' else None
                    outgoing = columns[0] if args.direction == 'OUT' else None
                    incoming = columns[0] if args.direction == 'IN' else None
                    repo = columns[1]
                    project = columns[2]
                elif len(columns) == 4:
                    outgoing = columns[0]
                    incoming = columns[1]
                    repo = columns[2]
                    project = columns[3]
                    either = None
                else:
                    outgoing = None
                    incoming = None
                    either = None
                    repo = columns[0]
                    project = columns[1]

                future = executor.submit(get_pr, project, repo, outgoing, incoming, either)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
