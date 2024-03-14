import json
from shared import arguments as arg, output, trace as trace, connection

DESCR = 'Retrieves all users from the Bitbucket Server.'
EPILOG = \
    'Each user is printed to a separate line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script, False)
    parser.add_argument('-f', '--filter', help='Filters on user name or email address containing the filter')
    parser.add_argument('fields', nargs='*', choices=['all', 'id', 'name', 'displayName', 'emailAddress'],
                        default='all', help='Display fields')
    parser.set_defaults(func=main)

def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    if isinstance(args.fields, str):
        if args.fields == 'all':
            fields = ['id', 'name', 'displayName', 'emailAddress']
        else:
            fields = [args.fields]
    else:
        fields = args.fields;
    token_header = "Bearer {}".format(env.token)
    page = 0
    is_last_page = False
    while not is_last_page:
        addr = "/rest/api/latest/users?start={}".format(page)
        if args.filter:
            addr = "{}&filter={}".format(addr, args.filter)
        output.print_debug(env, addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        output.print_debug(env, "addr={}".format(addr))
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            data = json.load(response)
            output.print_debug(env, "data={}".format(data))
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            for value in data['values']:
                output_line = ''
                for field in fields:
                    if field == 'all':
                        continue
                    v = value[field]
                    if output_line == '':
                        output_line = v
                    else:
                        output_line = "{}{}{}".format(output_line, env.sep, v)
                output.write(output_line)
            is_last_page = data['isLastPage']
            if not is_last_page:
                page = data['nextPageStart']
        else:
            output.print_error(env, addr, response, env.script)
            exit(2)
