from shared import connection
import json

from shared import arguments as arg, output, trace as trace
from shared.trace import trace_response
from jira import functions as cmn

DESCR = 'Retrieves named issues from the jira server.'
EPILOG = \
    'Each issue is printed to output on a separate line. The following ' \
    'columns are printed: id, key, project, created, type, status, creator, assignee, summary.'


def configure_parser(parser, script):
    arg.add_common(parser, 'JIRA', script)
    parser.add_argument('keys', metavar='KEYS', nargs="+", help='A list of issue keys')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')
    token_header = "Bearer {}".format(env.token)
    output_lines = []
    for key in args.keys:
        addr = "/rest/api/2/issue/{}".format(key)
        output.print_debug(env, addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Accept": "application/json;charset=UTF-8",
             "Accept-Charset": "UTF-8",
             "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        output.print_debug(env, "addr={}".format(addr))
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            issue = json.load(response)
            output.print_debug(env, "headers={}".format(response.getheaders()))
            output.print_debug(env, "response={}".format(json.dumps(issue)))
            env.trace and trace_response(uuid, env.script, verb, addr, response.status, issue)
            issue_id, project, issue_key, assigneeName, created, origin, status, issue_type, summary = \
                cmn.extract_issue_data(issue)
            output_lines.append(
                "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(issue_id, env.sep, project, env.sep, issue_key,
                                                            env.sep, created, env.sep, issue_type, env.sep, status,
                                                            env.sep, origin, env.sep, assigneeName, env.sep, summary))
        else:
            output.print_error(env, addr, response, env.script)
            exit(2)
    output.write(output_lines)
