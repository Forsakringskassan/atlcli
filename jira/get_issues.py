from shared import connection
import json
import os
import re
import sys
import urllib
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from shared import arguments as arg, output, trace as trace
from shared.trace import trace_response
from jira import functions as cmn

DESCR = 'For each board in input, lists all issues. Avoid this function because of horrible performance.'
EPILOG = \
    'Input is each board on a separate line. Output is input line followed by issue id and name. ' \
    'Pipe output to .'


def configure_parser(parser, script):
    arg.add_common(parser, 'JIRA', script)
    parser.add_argument('-c', '--count', action='store_true', help='Output number of issues instead of names')
    keys_help = 'A list of issue key regular expressions. Only issues matching any of the expressions are included'
    parser.add_argument('-n', '--names', nargs='+', help=keys_help)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')
    token_header = "Bearer {}".format(env.token)
    key_patterns = []
    if args.names is not None:
        for b in args.names:
            pattern = re.compile(b)
            key_patterns.append(pattern)

    def get_board_issues(line, board):
        result = []
        page = 0
        is_last_page = False
        count = 0
        while not is_last_page:
            params = {'startAt': page}
            query = urllib.parse.urlencode(params)
            addr = "/rest/agile/1.0/board/{}/issue?{}".format(board, query)
            output.print_debug(env, addr)
            conn = connection.create(env)
            h = {"User-Agent": env.version,
                 "Accept": "application/json",
                 "Authorization": token_header}
            verb = "GET"
            uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
            conn.request(verb, addr, headers=h)
            response = conn.getresponse()
            if response.status == 200:
                data = json.load(response)
                # cmn.print_debug(env, "response={}".format(data))
                startAt = data['startAt']
                maxResults = data['maxResults']
                total = data['total']
                output.print_debug(env,
                                   "startAt={}, maxResults={}, total={}, is_last_page={}".format(startAt, maxResults,
                                                                                                 total, is_last_page))
                env.trace and trace_response(uuid, env.script, verb, addr, response.status, data)
                for issue in data['issues']:
                    page += 1
                    issue_id, project, issue_key, assignee_name, created, origin, status, issue_type, summary = \
                        cmn.extract_issue_data(issue)
                    match = len(key_patterns) == 0
                    if not match:
                        for pattern in key_patterns:
                            if pattern.fullmatch(issue_key) is not None:
                                match = True
                                break
                    # cmn.print_debug(env, "issue_key={}, match={}".format(issue_key, match))
                    if match:
                        # cmn.print_debug(env, "issue={}".format(issue))
                        if args.count:
                            count += 1
                        else:
                            result.append("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(issue_id,
                                                                                          env.sep, project,
                                                                                          env.sep, issue_key,
                                                                                          env.sep, created,
                                                                                          env.sep, issue_type,
                                                                                          env.sep, status,
                                                                                          env.sep, origin,
                                                                                          env.sep, assignee_name,
                                                                                          env.sep, summary,
                                                                                          env.sep, line, ))
                    # if issue['state'] == args.state:
                is_last_page = page >= total

            else:
                output.print_error(env, addr, response, env.script)
                return None

        if args.count:
            result.append("{}{}{}".format(line, env.sep, count))
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 1:
                    stderr.write(
                        "\033[31m{}: Bad input, expected indata, input is only whitespace\033[0m{}".format(env.script,
                                                                                                           os.linesep))
                    exit(3)
                board = columns[0]
                future = executor.submit(get_board_issues, rstrip, board)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
