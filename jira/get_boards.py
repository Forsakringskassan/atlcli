from shared import connection
import json
import urllib.parse

from shared import arguments as arg, output, trace as trace

DESCR = 'Retrieves all boards from the Jira Server.'
EPILOG = \
    'Each board is printed to a separate line. First column is board id, second column is board name, ' \
    'third column is  board type.'


def configure_parser(parser, script):
    parser.add_argument('-n', '--name',
                        help='Filters results to boards that match or partially match the specified name.')
    parser.add_argument('-y', '--type',
                        help='Filters results to boards of the specified type. Valid values: scrum, kanban.')
    # -p switch is use for other purpose
    # project_help = 'Filters results to boards that are relevant to a project. Relevance meaning that the jql filter ' \
    #                'defined in board contains a reference to a project.'
    # parser.add_argument('-p', '--project', help=project_help)
    arg.add_common(parser, 'JIRA', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'JIRA')
    token_header = "Bearer {}".format(env.token)
    page = 0
    is_last_page = False
    while not is_last_page:
        params = {'startAt': page}
        if args.name:
            params['name'] = args.name
        if args.type:
            params['type'] = args.type
        # if args.project:
        #     params['projectKeyOrId'] = args.project
        query = urllib.parse.urlencode(params)
        addr = "/rest/agile/latest/board?%s" % query
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
            is_last_page = data['isLast']
            output.print_debug(env, "isLast={}".format(is_last_page))
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            for value in data['values']:
                page += 1
                # cmn.print_debug(env, "value={}".format(value))
                output_lines.append('{}{}{}{}{}'.format(value['id'], env.sep, value['name'], env.sep, value['type']))
            output.write(output_lines)
        else:
            output.print_error(env, addr, response, env.script)
            exit(2)
