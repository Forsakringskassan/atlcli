import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr

from shared import arguments as arg, trace as trace, output, connection
from bitbucket import functions as cmn

DESCR = 'Prints affected file names of a pull request for each pull request in input.'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Only OPEN ' \
        'pull request are included in output. Output is each affected file on a separate line followed by the ' \
         'input line.' \
        'The file name is the name in the to-branch, but if the file is deleted, ' \
        'it is the name from the from-branch. Since the underlying api is not paged, data could be truncated, this ' \
        'is indicated by the first line in output having TRUNCATED instead of a file name'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def get_files(project, repo, pr_id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, pr_id, env.script)
        if pr_data is None:
            return None
        if pr_data['state'] != 'OPEN':
            return []

        addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/diff".format(project, repo, pr_id)
        conn = connection.create(env)
        h = {"User-Agent": env.version,
             "Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        result = []
        if response.status < 500:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            if data['truncated']:
                result.append('TRUNCATED{}{}'.format(env.sep, line))
            if response.status == 200:
                for diff in data['diffs']:
                    dest = diff['destination']
                    # print(dest)
                    dest = dest if dest is not None else diff['source']
                    fn = dest['toString'] if dest is not None else None
                    result.append('{}{}{}'.format(fn, env.sep, line))
                return result
            else:
                output.print_error(env, addr, response, env.script)
                return None

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 5:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 5 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                pr_id = columns[0]
                repo = columns[3]
                project = columns[4]
                future = executor.submit(get_files, project, repo, pr_id, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
