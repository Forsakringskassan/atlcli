import json
import os
from concurrent.futures import ThreadPoolExecutor
from sys import stdin, stderr
from shared import arguments as arg, trace as trace, output, connection
from bitbucket import functions as cmn

DESCR = 'Foreach two branch names in input, filters merged branch pairs.'
EPILOG = 'Each input line starts with the two branch names, followed by project and repo names. ' \
        'The first branch name is the outgoing branch, and the second is the incoming branch.' \
        'The last commit of the outgoing branch is compared to all commits in the incoming branch. If this ' \
        'commit is found, a merge has been performed, and the branches are included in output. Also if ' \
        'the incoming branch is a parent of the outgoing branch, and there are no changes, this ' \
        'is considered a merge, since they are equal. ' \
        'Output is same as input. Pipe output to get-commits.py or ' \
         'delete-branches.py or get-file-names.py or create-pr.py or get-pr.py.'


def configure_parser(parser, script):
    arg.add_common(parser, 'BITBUCKET', script)
    parser.add_argument('-i', '--invert', action='store_true',
                        help='Invert results, report unmerged repos.')
    parser.set_defaults(func=main)


def main(parser, args):
    env = arg.get_common_arguments(parser, args, 'BITBUCKET')
    token_header = "Bearer {}".format(env.token)

    def filter_merged(project, repo, from_branch, to_branch, line):
        result = []
        names = [from_branch, to_branch]
        [from_record, to_record] = \
            cmn.get_branch_or_tag(env, project, repo, 'branchestags', names, env.script)
        # print('from_record={}, to_record={}'.format(from_record['id'], to_record['id']))
        from_commit = from_record['latestCommit']
        to_commit = to_record['latestCommit']
        from_is_parent_to = is_parent(project, repo, from_commit, to_commit, [])
        to_is_parent_from = \
            is_parent(project, repo, to_commit, from_commit, []) if not from_is_parent_to else False
        unchanged = to_is_parent_from and check_unchanged(project, repo, from_commit, to_commit)
        merged = from_is_parent_to or unchanged
        if (merged and not args.invert) or (not merged and args.invert):
            result.append(line)
        return result

    def check_unchanged(project, repo, from_commit, to_commit):
        addr = "/rest/api/1.0/projects/{}/repos/{}/commits/{}/changes?since={}".format(project, repo, from_commit,
                                                                                       to_commit)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            return len(data['values']) == 0
        else:
            output.print_error(env, addr, response, env.script)
            return None

    def is_parent(project, repo, parent_commit, child_commit, seen_commits):
        if parent_commit == child_commit:
            return True
        addr = "/rest/api/1.0/projects/{}/repos/{}/commits/{}".format(project, repo, child_commit)
        conn = connection.create(env)
        h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
        verb = "GET"
        uuid = trace.trace_request(env.script, verb, addr) if env.trace else None
        conn.request(verb, addr, headers=h)
        response = conn.getresponse()
        if response.status == 200:
            data = json.load(response)
            env.trace and trace.trace_response(uuid, env.script, verb, addr, response.status, data)
            parents = []
            items = data['parents']
            for item in items:
                commit = item['id']
                if not commit in seen_commits:
                    parents.append(commit)
                    seen_commits.append(commit)
            for p in parents:
                if parent_commit == p:
                    return True
            for p in parents:
                r = is_parent(project, repo, parent_commit, p, seen_commits)
                if r:
                    return True
            return False
        else:
            output.print_error(env, addr, response, env.script)
            return None

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
                from_branch = columns[0]
                to_branch = columns[1]
                repo = columns[2]
                project = columns[3]
                future = executor.submit(filter_merged, project, repo, from_branch, to_branch, rstrip)
                futures.append(future)
            input.close()
            for future in futures:
                future.done()
                output_lines = future.result()
                if output_lines is None:
                    exit(2)
                output.write(output_lines)
