from shared import connection
import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, output, trace as trace
from jira import functions as cmn

WHITESPACE_ERROR = "\033[31m{}: Bad input, expected indata, input is only whitespace\033[0m{}"
DESCR = 'For each issue in input, lists all subtasks.'
EPILOG = \
    'Input is each issue on a separate line. Output is input line prepended by data for the subtask. The following ' \
    'columns are printed: id, key, created, type, status, creator, assignee, summary.' \
    'Pipe output to .'


def configure_parser(parser, script):
    arg.add_common(parser, 'JIRA', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')

    def get_subtasks(line, issue):
        token_header = "Bearer {}".format(env.token)
        result = []
        issue_addr = "/rest/api/2/issue/{}".format(issue)
        output.print_debug(env, issue_addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, issue_addr) if env.trace else None
        conn.request(verb, issue_addr, headers=h)
        issue_response = conn.getresponse()
        if issue_response.status == 200:
            issue_data = json.load(issue_response)
            issue_fields = issue_data['fields']
            for subtask in issue_fields['subtasks']:
                subtask_id = subtask['id']
                subtask_line = cmn.get_subtask(env, line, subtask_id)
                if subtask_line is not None:
                    result.append(subtask_line)

        else:
            output.print_error(env, issue_addr, issue_response, env.script)
            return None
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 1:
                    stderr.write(WHITESPACE_ERROR.format(env.script, os.linesep))
                    exit(3)
                issue_id = columns[0]
                future = executor.submit(get_subtasks, rstrip, issue_id)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
