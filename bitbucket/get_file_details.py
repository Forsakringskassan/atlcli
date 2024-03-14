import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, output, conversion as conversion, connection

DESCR = 'Lists file details for each file name in input.'
EPILOG = 'Each input line starts with the file name, followed by branch name and lastly the project name. '\
        'Output is each input line prepended with last modified date, committer, message and commit id in separate columns.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-s', '--substitute', type=str, default='   ',
                        help="Replacement pattern for separator. Default is 3 spaces")
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)
    separator_pattern = re.compile(env.sep)
    newline_pattern = re.compile('\n')
    sub = bytes(args.substitute, "utf-8").decode("unicode_escape")
    cache = {}
    mutex = threading.Lock()

    def get_file_details(line, project, repo, branch, name):
        result = []
        catalog, basename = os.path.split(name)
        cache_key = "{}-{}-{}-{}".format(project, repo, branch, catalog)
        if cache_key in cache.keys():
            data = cache[cache_key]
        else:
            mutex.acquire()
            if cache_key in cache.keys():
                data = cache[cache_key]
                mutex.release()
            else:
                addr = "/rest/api/1.0/projects/{}/repos/{}/last-modified/{}?at={}".format(project, repo, catalog,
                                                                                          branch)
                # print(addr)
                conn = connection.create(env)
                h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
                verb = "GET"
                uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
                conn.request(verb, addr, headers=h)
                response = conn.getresponse()
                if response.status == 200:
                    data = json.load(response)
                    cache[cache_key] = data
                    mutex.release()
                    env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
                else:
                    mutex.release()
                    output.print_error(env, addr, response, env.script)
                    return None
        files = data["files"]
        file = files[basename]
        commit = file['id']
        committer = file['committer']
        name = committer['emailAddress']
        if name is None or len(name.strip()) == 0:
            name = committer['name']
        time = conversion.to_time(file['committerTimestamp'])
        message = re.sub(newline_pattern, ' ', re.sub(separator_pattern, sub, file['message']))
        result.append(
            "{}{}{}{}{}{}{}{}{}".format(time, env.sep, name, env.sep, message, env.sep, commit, env.sep, line))
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 3:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 3 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                project = columns[3]
                repo = columns[2]
                branch = columns[1]
                name = columns[0]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_file_details, rstrip, project, repo, branch, name)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
