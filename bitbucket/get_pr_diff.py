from shared import connection
import os
import re
from concurrent.futures import ThreadPoolExecutor
from sys import stderr, stdin

from shared import arguments as arg, conversion as conversion, output
from bitbucket import functions as cmn

DESCR = 'Prints pull request diffs for each pull request in input.'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name.' \
        'Output is each line in diff followed by the input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-s', '--substitute', type=str, default='   ',
                        help="Replacement pattern for separator. Default is 3 spaces")
    parser.add_argument('-e', '--encoding', type=str, default='iso-8859-1', help="Fallback file encoding.")
    parser.add_argument('-n', '--newline', type=str, default="\r", help="Line ending char, default is \\r.")
    parser.add_argument('-d', '--directory', type=str, default='.', help="Trace directory.")
    parser.set_defaults(func=main)

def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    sub = bytes(args.substitute, "utf-8").decode("unicode_escape")
    separator_pattern = re.compile(env.sep)
    token_header = "Bearer {}".format(env.token)
    newline = bytes(args.newline, 'utf-8')
    fallback = args.encoding

    def get_pr_diff(line, project, repo, id):
        encoding = 'UTF-8'
        addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}.diff".format(project, repo, id)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "text/plain", "Authorization": token_header}
        verb = "GET"
        # uuid = cmn.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            f = None
            if env.trace:
                try:
                    filename = conversion.to_file_name(args.directory, addr)
                    f = open(filename, 'wb')
                except:
                    stderr.write("\033[31m{}: Could not create file: {}\033[0m\n".format(env.script, filename))
            result = []
            for response_lines in response:
                # Most lines are correctly split here, the rest are taken care of with split method
                lines = response_lines.split(newline)
                for l in lines:
                    if env.trace and f is not None:
                        f.write(l)
                    l2 = None
                    while l2 is None:
                        l2, e = cmn.decode(l, encoding)
                        if l2 is None:
                            if encoding == fallback:
                                stderr.write(
                                    "\033[31m{}: Could not decode {}: {} \033[0m\n".format(env.script, addr, str(e)))
                                if env.trace and f is not None:
                                    f.close()
                                return None
                            else:
                                encoding = fallback
                    if len(l2) != 0:
                        result.append("{}{}{}".format(re.sub(separator_pattern, sub, l2), env.sep, line))
            if env.trace and f is not None:
                f.close()
            return result

        else:
            output.print_error(env, addr, response, env.script)
            return []

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
                id = columns[0]
                repo = columns[3]
                project = columns[4]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_pr_diff, rstrip, project, repo, id)
                futures.append(future)
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
