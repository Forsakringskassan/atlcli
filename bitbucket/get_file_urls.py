import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from sys import stderr, stdin
from shared import arguments as arg, output

DESCR = 'Lists download url for each file name in input.'
EPILOG = 'Each input line starts with the file name, followed by branch or tag name, repo name and lastly the ' \
         'project name. Output is download url followed by input line. Pipe output to get-file-content.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')

    def get_files(file, branch, repo, project, line):
        result = []
        try:
            f = urllib.parse.quote(file)
        except:
            stderr.write("\033[31m{}: Could not urlencode {}\033[0m{}".format(env.script, file, os.linesep))
            return result
        addr = "https://{}/projects/{}/repos/{}/raw/{}?at={}".format(env.url, project, repo, f, branch)
        # print(addr)
        result.append('{}{}{}'.format(addr, env.sep, line))
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                if len(columns) < 4:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 4 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                file = columns[0]
                branch = columns[1]
                repo = columns[2]
                project = columns[3]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_files, file, branch, repo, project, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
