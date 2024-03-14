import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, output, connection

DESCR = 'Lists or searches file names for each branch in input.'
EPILOG = 'Each input line starts with a branch or tag name, followed by repo name and then the project name. '\
        'Output is input line prepended with each found file. Pipe output to get-file-urls.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    max_help = \
        'Output maximum max of lines only. Use this option to filter repos with a given file by giving 1 as parameter.'
    parser.add_argument('-m', '--max', type=int, help=max_help)
    parser.add_argument('-c', '--count', action='store_true', help='Output number of matching files instead of names')
    name_help = 'A regular expression defining the file names to search for. The whole path is used ' \
                'in the search, that is if the regular expression matches eanything in the path to the file it ' \
                'is included.'
    parser.add_argument('-n', '--name', default='.', help=name_help)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)
    pattern = re.compile(args.name)

    def get_files(project, repo, branch, line):
        result = []
        page = 0
        count = 0
        is_last_page = False
        while not is_last_page:
            addr = "/rest/api/1.0/projects/{}/repos/{}/files?at={}&start={}".format(project, repo, branch, page)
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
                    # print(value)
                    if pattern.search(value) is not None:
                        count += 1
                        if not args.count:
                            result.append("{}{}{}".format(value, env.sep, line))
                        if args.max is not None and args.max == count:
                            is_last_page = True
                            break
                is_last_page = is_last_page or data['isLastPage']
                if not is_last_page:
                    page = data['nextPageStart']
            else:
                output.print_error(env, addr, response, env.script)
                return None

        if args.count:
            result.append('{}{}{}'.format(count, env.sep, line))
        return result


    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 3:
                    stderr.write("\033[31m{}: Bad input, expected at least 3 columns: {}\033[0m{}".format(env.script,
                                                                                                          line,
                                                                                                          os.linesep))
                    exit(3)
                branch = columns[0]
                repo = columns[1]
                project = columns[2]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_files, project, repo, branch, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
