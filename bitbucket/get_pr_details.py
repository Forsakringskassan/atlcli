import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, conversion as conversion, output
from bitbucket import functions as cmn

DESCR = \
    'Prints pull request details for each pull request in input.'
EPILOG = 'Each input starts with the pull request id, followed by two branch names (ignored) and then the repo name' \
         'and lastly the project name. Output is ' \
         'title, created time, state, version, author, reviewer, status, canMerge, link to pull request in bitbucket, '\
         'followed by input line.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-j', '--json', action='store_true', help='Outputs json string instead of columns.')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')

    def get_pr_details(project, repo, id, line):
        pr_data, merge_data = cmn.get_pr_and_merge(env, project, repo, id, env.script)
        if pr_data is None:
            return None
        created = conversion.to_time(pr_data['createdDate'])
        if len(pr_data['reviewers']) != 0:
            reviewer0 = None
            status0 = None
            for r in pr_data['reviewers']:
                if reviewer0 is None:
                    reviewer0 = r
                    status0 = r['status']
                else:
                    status = r['status']
                    if status == 'UNAPPROVED':  # , NEEDS_WORK, or APPROVED
                        reviewer0 = r
                        status0 = status
                    elif status == 'NEEDS_WORK' and status0 != 'UNAPPROVED':
                        reviewer0 = r
                        status0 = status
                    elif status == 'APPROVED' and status0 != 'UNAPPROVED' and status0 != 'NEEDS_WORK':
                        reviewer0 = r
                        status0 = status
            reviewer = reviewer0['user']['emailAddress']
            if reviewer is None or len(reviewer.strip()) == 0:
                reviewer = reviewer0['user']['name']
            status = status0
        else:
            reviewer = 'None'
            status = 'N/A'
        title = pr_data['title']
        state = pr_data['state']
        version = pr_data['version']
        author = pr_data['author']['user']['emailAddress']
        if author is None or len(author.strip()) == 0:
            author = pr_data['author']['user']['name']
        can_merge = merge_data['canMerge'] if merge_data is not None else 'N/A'
        link = pr_data['links']['self'][0]['href']
        result = []
        if args.json:
            details = {
                'title': title,
                'created': created,
                'state': state,
                'version': version,
                'author': author,
                'reviewer': reviewer,
                'status': status,
                'canMerge': can_merge,
                'link': link
            }
            result.append('{}{}{}'.format(json.dumps(details), env.sep, line))
        else:
            result.append('{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(title, env.sep,
                                                                          created, env.sep,
                                                                          state, env.sep,
                                                                          version, env.sep,
                                                                          author, env.sep,
                                                                          reviewer, env.sep,
                                                                          status, env.sep,
                                                                          can_merge, env.sep,
                                                                          link, env.sep,
                                                                          line))
        return result

    with open(args.file) if args.file else stdin as input:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for line in input:
                columns = line.rstrip().split(env.sep)
                if len(columns) < 5:
                    stderr.write(
                        "\033[31m{}: Bad input, expected at least 5 columns: {}\033[0m{}".format(env.script, line,
                                                                                                 os.linesep))
                    exit(3)
                id = columns[0]
                repo = columns[3]
                project = columns[4]
                # print(" {} {} {}".format(project, repo, name))
                future = executor.submit(get_pr_details, project, repo, id, line.rstrip('\n'))
                futures.append(future)
            for future in futures:
                future.done()
                result = future.result()
                if result is None:
                    exit(2)
                output.write(result)
