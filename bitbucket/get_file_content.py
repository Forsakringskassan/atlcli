import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from sys import stderr, stdin
from shared import arguments as arg, conversion as conversion, output
from bitbucket import functions as cmn


def main_count(parser, args):
    main(parser, args, True, None, None)


def main_lines(parser, args):
    before = args.before_context
    after = args.after_context
    main(parser, args, False, before, after)


DESCR = 'Downloads files and searches file contents. Matching rows, or count, are output.'
EPILOG = 'Each inputline should have the download url in first column. Each file is downloaded and lines are matched. ' \
         'Default encoding is ' \
         'UTF-8. If decoding fails, the fallback encoding is used. If env.trace is specified, each ' \
         'downloaded file is saved in a separate file, using the url as file name.'


def configure_parser(parser, script):
    global count
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-s', '--substitute', type=str, default='   ',
                        help="Replacement pattern for separator. Default is 3 spaces.")
    parser.add_argument('-e', '--encoding', type=str, default='iso-8859-1', help="Fallback file encoding.")
    parser.add_argument('-d', '--directory', type=str, default='.', help="Trace file directory.")
    parser.add_argument('-n', '--newline', type=str, default="\r", help="Line ending char, default is \\r.")
    parser.add_argument('-v', '--invert-match', action='store_true', help="Select non-matching lines.")
    subparser = parser.add_subparsers(dest='command', required=True,
                                      help="'lines' will output the matching lines. 'count' will output number of matching lines.")
    epilog_lines = 'Two columns are added to the input line, line number and line contents.'
    lines = subparser.add_parser('lines', description='Outputs all matching lines.', epilog=epilog_lines)
    lines.add_argument('pattern', metavar='PATTERN',
                       help='A regular expression matching the full line.')
    lines.add_argument('-B', '--before-context', type=int, default=0,
                       help='Print BEFORE_CONTEXT lines of leading context.')
    lines.add_argument('-A', '--after-context', type=int, default=0,
                       help='Print AFTER_CONTEXT lines of trailing context.')
    lines.set_defaults(func=main_lines)
    epilog_count = 'One column is added to the input line, the number of matching lines.'
    count = subparser.add_parser('count', description='Outputs number of matching lines.', epilog=epilog_count)
    count.add_argument('pattern', metavar='PATTERN',
                       help='A regular expression matching the full line.')
    count.set_defaults(func=main_count)


def main(parser, args, counting, before, after):
    # global env, pattern, token_header, sub, separator_pattern, fallback, newline, invert, rstrip
    # sname = os.path.basename(argv[0])
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    pattern = re.compile(args.pattern)
    token_header = "Bearer {}".format(env.token)
    sub = bytes(args.substitute, "utf-8").decode("unicode_escape")
    separator_pattern = re.compile(env.sep)
    fallback = args.encoding
    newline = bytes(args.newline, 'utf-8')
    invert = args.invert_match

    def get_file_lines(input_line, download_url, counting, before, after):
        encoding = 'UTF-8'
        f = None
        if env.trace:
            try:
                #  $ reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem"
                #  HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
                #  LongPathsEnabled    REG_DWORD    0x1

                filename = conversion.to_file_name(args.directory, download_url)
                f = open(filename, 'wb')
            except Exception as e:
                stderr.write(f"\033[31m{env.script}: Could not create file: {filename} : {e}\033[0m\n")
                raise e
        result = []
        lines = []
        matches = []
        h = {b"User-Agent": env.version, b"Authorization": token_header}
        output.print_debug(env, download_url)
        output.stdout.flush()
        request = urllib.request.Request(download_url, headers=h, data=None, method="GET")
        response = urllib.request.urlopen(request)
        i = 0
        if response.status == 200:
            for response_lines in response:
                # Most input_lines are correctly split here, the rest are taken care of with split method
                input_lines = response_lines.split(newline)
                for l in input_lines:
                    if env.trace and f is not None:
                        f.write(l)
                    l2 = None
                    while l2 is None:
                        l2, e = cmn.decode(l, encoding)
                        if l2 is None:
                            if encoding == fallback:
                                stderr.write(
                                    "\033[31m{}: Could not decode {}: {} \033[0m\n".format(env.script, download_url,
                                                                                           str(e)))
                                if env.trace and f is not None:
                                    f.close()
                                return None
                            else:
                                encoding = fallback

                m = pattern.fullmatch(l2)
                lines.append(l2)
                if (m is not None and not invert) or (m is None and invert):
                    if (not i in matches) and i >= 0:
                        matches.append(i)
                    if not counting:
                        for j in range(i - before, i + 1):
                            if not j in matches:
                                matches.append(j)
                        for j in range(i, i + after + 1):
                            if not j in matches:
                                matches.append(j)
                i += 1
            if counting:
                result.append('{}{}{}'.format(str(len(matches)), env.sep, input_line))
            else:
                matches.sort()
                for i in matches:
                    if i < len(lines):
                        result.append('{}{}{}{}{}'.format(i,
                                                          env.sep,
                                                          re.sub(separator_pattern, sub, lines[i]),
                                                          env.sep,
                                                          input_line))

        else:
            output.print_error(env, download_url, response, env.script)
            return None
        if env.trace and f is not None:
            f.close()
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                rstrip = line.rstrip()
                columns = rstrip.split(env.sep)
                download_url = columns[0]
                # print("download_url = {}".format(download_url))
                future = executor.submit(get_file_lines, rstrip, download_url, counting, before, after)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
