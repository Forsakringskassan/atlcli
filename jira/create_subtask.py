from shared import connection
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from shared import arguments as arg, output, trace as trace
from jira import functions as cmn

WHITESPACE_ERROR = "\033[31m{}: Bad input, expected indata, input is only whitespace\033[0m{}"
DESCR = 'Creates a jira subtask for each issue in input.'
EPILOG = \
    'Output has the same format as get-subtasks.py, the newly created issue is followed by its parent issue.'


def configure_parser(parser, script):
    arg.add_common(parser, 'JIRA', script)
    parser.add_argument('summary', metavar='SUMMARY', help='The subtask summary')
    parser.add_argument('description', metavar='DESCRIPTION', help='The subtask description')
    parser.add_argument('-b', '--bug', action='store_true', help='Creates a bug subtask')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')
    token_header = "Bearer {}".format(env.token)

    def create_subtask(line, issue, project):
        result = []
        addr = "/rest/api/2/issue"
        output.print_debug(env, addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        output.print_debug(env, "headers={}".format(h))
        verb = "POST"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        body = {
            'fields': {
                'project': {
                    'id': project,
                },
                'parent': {
                    'id': issue,
                },
                'summary': args.summary,
                'description': args.description,
                'issuetype': {
                    'name': 'Bug (sub-task)' if args.bug else 'Sub-task',
                    'subtask': True,
                }
            }
        }
        message = json.dumps(body)
        output.print_debug(env, "message={}".format(message))

        conn.request(verb, addr, headers=h, body=message)
        create_response = conn.getresponse()
        if create_response.status == 201:
            output.print_debug(env, "headers={}".format(create_response.getheaders()))
            created_data = json.load(create_response)
            created_id = created_data['id']
            subtask_line = cmn.get_subtask(env, line, created_id)
            if subtask_line is not None:
                result.append(subtask_line)
        else:
            output.print_error(env, addr, create_response, env.script)
            return None
        return result

    with open(args.file) if args.file else sys.stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 1:
                    sys.stderr.write(WHITESPACE_ERROR.format(env.script, os.linesep))
                    exit(3)
                issue_id = columns[0]
                project = columns[1]
                future = executor.submit(create_subtask, rstrip, issue_id, project)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
