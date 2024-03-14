import json
import re
from shared import arguments as arg, connection, trace as trace, output


ADDR_TEMPLATE = "/rest/api/1.0/projects?start={}"

DESCR = 'Retrieves all projects from the Bitbucket Server.'
EPILOG = 'Each project is printed to a separate line. Pipe output to get-repos.py.'


def configure_parser(parser, script_name):
    arg.add_common(parser, 'BITBUCKET', script_name, False)
    format_help = 'Output format. KEY means project key, NAME is project name, BOTH means key:name'
    parser.add_argument('-f', '--format', default='KEY', choices=['KEY', 'NAME', 'BOTH'], help=format_help)
    names_help = 'Space separated list of regular expressions defining project keys. Unlike other script, this one ' \
                 'affects trace data as well.'
    parser.add_argument('-n', '--names', nargs='+', help=names_help)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)
    patterns = []
    if args.names is not None:
        for t in args.names:
            pattern = re.compile(t)
            patterns.append(pattern)
    page = 0
    is_last_page = False
    while not is_last_page:
        addr = ADDR_TEMPLATE.format(page)
        # print(addr)
        output.print_debug(env, addr)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        output.print_debug(env, "addr={}".format(addr))
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        patterns_len = len(patterns)
        if response.status == 200:
            lines = []
            data = json.load(response)
            page_match = patterns_len == 0
            for value in data['values']:
                key = value['key']
                name = value['name']
                key_match = patterns_len == 0
                if patterns_len > 0:
                    for p in patterns:
                        if p.fullmatch(key):
                            key_match = True
                            page_match = True
                if not key_match:
                    continue
                if args.format == 'BOTH':
                    lines.append("{}:{}".format(key, name))
                elif args.format == 'NAME':
                    lines.append(name)
                else:
                    lines.append(key)
            # We limit trace data to matching projects.
            if env.trace and page_match:
                # This code depends on giving a -n value matchin only one project
                addr0 = ADDR_TEMPLATE.format(0)
                uuid = trace.trace_request(env.script, verb, addr0) if env.trace else None
                data['isLastPage'] = True
                data['start'] = 0
                data['nextPageStart'] = 25
                env.trace and trace.trace_response(uuid, env.script, verb, addr0, response.status, data)

            output.write(lines)
            is_last_page = data['isLastPage']
            if not is_last_page:
                page = data['nextPageStart']
        else:
            output.print_error(env, addr, response, env.script)
            exit(2)

