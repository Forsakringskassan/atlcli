from shared import connection
import json

from shared import arguments as arg, output, trace as trace
from shared.trace import trace_response

DESCR = 'Retrieves all projects from the Jira Server.'
EPILOG = \
    'Each project is printed to a separate line. First column is project id, second column is project key, ' \
    'third column is project name.'


def configure_parser(parser, script):
    arg.add_common(parser, 'JIRA', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')
    token_header = "Bearer {}".format(env.token)
    addr = "/rest/api/2/project"
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
        output.print_debug(env, "headers={}".format(response.getheaders()))
        output_lines = []
        data = json.load(response)
        output.print_debug(env, "response={}".format(data))
        env.trace and trace_response(uuid, env.script, verb, addr, response.status, data)
        for value in data:
            # cmn.print_debug(env, "value={}".format(value))
            output_lines.append('{}{}{}{}{}'.format(value['id'], env.sep, value['key'], env.sep, value['name']))
        output.write(output_lines)
    else:
        output.print_error(env, addr, response, env.script)
        exit(2)
