import argparse
import logging
import os
import sys
import coloredlogs
import atlassiancli

from shared import eformatter
from shared.commonlogging import LOG_LEVELS, nameToLevel, COLOREDLOGS_LOG_FORMAT, LOG_FORMAT
from tools import compare_versions, count_group_by, get_version, join_columns, minus_columns, order_by, \
    select_columns, sum_group_by, union, where_columns, where_matches
from jira import get_jprojects, get_issues, get_issue, get_boards, get_subtasks, create_subtask
from bitbucket import get_projects, get_repos, get_branches, get_branches_or_tags, get_tags, get_commits, \
    get_file_names, get_file_details, get_file_urls, get_clone_urls, get_commit_details, get_pr, get_pr_details, \
    get_pr_diff, get_pr_files, get_users, get_file_content, filter_branches, filter_merged, filter_pr, create_branches,\
    delete_branches, create_pr, delete_pr, put_pr, merge_pr, create_tags

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')


def setup_parser():
    parser = argparse.ArgumentParser(usage='atlcli', description="Command line interface to atlassian servers.",
                                     formatter_class=eformatter.Formatter)
    parser.add_argument('-l', '--loglevel', choices=LOG_LEVELS, default='info', help='Sets logging level.')
    parser.add_argument('-v', '--version', action='store_true', help='Prints current version and exits.')
    subparser = parser.add_subparsers(dest='domain', required=False)

    bitbucket_parser = subparser.add_parser("bitb", description='Bitbucket commands.')
    bitbucket = bitbucket_parser.add_subparsers(dest='bitbucket-command', required=True)
    configure_bitbucket(bitbucket)

    jira_parser = subparser.add_parser("jira", description='Jira commands.')
    jira = jira_parser.add_subparsers(dest='jira-command', required=True)
    configure_jira(jira)

    tools_parser = subparser.add_parser("tool", description='Tool commands.')
    tools = tools_parser.add_subparsers(dest='tool-command', required=True)
    configure_tools(tools)

    return parser


def configure_tools(tools):
    # compare-versions
    compare_versions_parser = tools.add_parser("compare-versions",
                                               description=compare_versions.DESCR,
                                               epilog=compare_versions.EPILOG)
    compare_versions.configure_parser(compare_versions_parser, "compare-versions")
    # count-group-by
    count_group_by_parser = tools.add_parser("count-group-by",
                                             description=count_group_by.DESCR,
                                             epilog=count_group_by.EPILOG)
    count_group_by.configure_parser(count_group_by_parser, "count-group-by")
    # get-version
    get_version_parser = tools.add_parser("get-version", description=get_version.DESCR, epilog=get_version.EPILOG)
    get_version.configure_parser(get_version_parser, "get-version")
    # join-columns
    join_columns_parser = tools.add_parser("join-columns", description=join_columns.DESCR, epilog=join_columns.EPILOG)
    join_columns.configure_parser(join_columns_parser, "join-columns")
    # minus-columns
    minus_columns_parser = tools.add_parser("minus-columns",
                                            description=minus_columns.DESCR,
                                            epilog=minus_columns.EPILOG)
    minus_columns.configure_parser(minus_columns_parser, "minus-columns")
    # order-by
    order_by_parser = tools.add_parser("order-by", description=order_by.DESCR, epilog=order_by.EPILOG)
    order_by.configure_parser(order_by_parser, "order-by")
    # select-columns
    select_columns_parser = tools.add_parser("select-columns",
                                             description=select_columns.DESCR,
                                             epilog=select_columns.EPILOG)
    select_columns.configure_parser(select_columns_parser, "select-columns")
    # sum-group-by
    sum_group_by_parser = tools.add_parser("sum-group-by",
                                           description=sum_group_by.DESCR,
                                           epilog=sum_group_by.EPILOG)
    sum_group_by.configure_parser(sum_group_by_parser, "sum-group-by")
    # union
    union_parser = tools.add_parser("union", description=union.DESCR, epilog=union.EPILOG)
    union.configure_parser(union_parser, "union")
    # where-columns
    where_columns_parser = tools.add_parser("where-columns",
                                            description=where_columns.DESCR,
                                            epilog=where_columns.EPILOG)
    where_columns.configure_parser(where_columns_parser, "where-columns")
    # where-matches
    where_matches_parser = tools.add_parser("where-matches",
                                            description=where_matches.DESCR,
                                            epilog=where_matches.EPILOG)
    where_matches.configure_parser(where_matches_parser, "where-matches")


def configure_jira(jira):
    # get-jprojects
    jprojects_parser = jira.add_parser("get-projects", description=get_jprojects.DESCR, epilog=get_jprojects.EPILOG)
    get_jprojects.configure_parser(jprojects_parser, "get-projects")
    # get-issues
    issues_parser = jira.add_parser("get-issues", description=get_issues.DESCR, epilog=get_issues.EPILOG)
    get_issues.configure_parser(issues_parser, "get-issues")
    # get-issue
    issue_parser = jira.add_parser("get-issue", description=get_issue.DESCR, epilog=get_issue.EPILOG)
    get_issue.configure_parser(issue_parser, "get-issue")
    # get-boards
    boards_parser = jira.add_parser("get-boards", description=get_boards.DESCR, epilog=get_boards.EPILOG)
    get_boards.configure_parser(boards_parser, "get-boards")
    # get-subtasks
    subtasks_parser = jira.add_parser("get-subtasks", description=get_subtasks.DESCR, epilog=get_subtasks.EPILOG)
    get_subtasks.configure_parser(subtasks_parser, "get-subtasks")
    # create-subtask
    subtask_parser = jira.add_parser("create-subtask", description=create_subtask.DESCR, epilog=create_subtask.EPILOG)
    create_subtask.configure_parser(subtask_parser, "create-subtask")


def configure_bitbucket(bitbucket):
    # get-users
    users = bitbucket.add_parser("get-users", description=get_users.DESCR, epilog=get_users.EPILOG)
    get_users.configure_parser(users, "get-users")
    # get-projects
    projects = bitbucket.add_parser("get-projects", description=get_projects.DESCR, epilog=get_projects.EPILOG)
    get_projects.configure_parser(projects, "get-projects")
    # get-repos
    repos = bitbucket.add_parser("get-repos", description=get_repos.DESCR, epilog=get_repos.EPILOG)
    get_repos.configure_parser(repos, "get-repos")
    # get-clone-urls
    clone_urls = bitbucket.add_parser("get-clone-urls", description=get_clone_urls.DESCR, epilog=get_clone_urls.EPILOG)
    get_clone_urls.configure_parser(clone_urls, "get-clone-urls")
    # get-branches
    branches = bitbucket.add_parser("get-branches", description=get_branches.DESCR, epilog=get_branches.EPILOG)
    get_branches.configure_parser(branches, "get-branches")
    # get-branches-or-tags
    branches_or_tags = bitbucket.add_parser("get-branches-or-tags",
                                            description=get_branches_or_tags.DESCR,
                                            epilog=get_branches_or_tags.EPILOG)
    get_branches_or_tags.configure_parser(branches_or_tags, "get-branches-or-tags")
    # get-tags
    tags = bitbucket.add_parser("get-tags", description=get_tags.DESCR, epilog=get_tags.EPILOG)
    get_tags.configure_parser(tags, "get-tags")
    # get-commits
    commits = bitbucket.add_parser("get-commits", description=get_commits.DESCR, epilog=get_commits.EPILOG)
    get_commits.configure_parser(commits, "get-commits")
    # get-commit-details
    commit_details = bitbucket.add_parser("get-commit-details",
                                          description=get_commit_details.DESCR,
                                          epilog=get_commit_details.EPILOG)
    get_commit_details.configure_parser(commit_details, "get-commit-details")
    # get-file-names
    file_names = bitbucket.add_parser("get-file-names", description=get_file_names.DESCR, epilog=get_file_names.EPILOG)
    get_file_names.configure_parser(file_names, "get-file-names")
    # get-file-details
    file_names = bitbucket.add_parser("get-file-details",
                                      description=get_file_details.DESCR,
                                      epilog=get_file_details.EPILOG)
    get_file_details.configure_parser(file_names, "get-file-details")
    # get-file-urls
    file_urls = bitbucket.add_parser("get-file-urls", description=get_file_urls.DESCR, epilog=get_file_urls.EPILOG)
    get_file_urls.configure_parser(file_urls, "get-file-urls")
    # get-file-content
    file_content = bitbucket.add_parser("get-file-content",
                                        description=get_file_content.DESCR,
                                        epilog=get_file_content.EPILOG)
    get_file_content.configure_parser(file_content, "get-file-content")
    # get-pr
    pr = bitbucket.add_parser("get-pr", description=get_pr.DESCR, epilog=get_pr.EPILOG)
    get_pr.configure_parser(pr, "get-pr")
    # get-pr-details
    pr_details = bitbucket.add_parser("get-pr-details", description=get_pr_details.DESCR, epilog=get_pr_details.EPILOG)
    get_pr_details.configure_parser(pr_details, "get-pr-details")
    # get-pr-diff
    pr_diff = bitbucket.add_parser("get-pr-diff", description=get_pr_diff.DESCR, epilog=get_pr_diff.EPILOG)
    get_pr_diff.configure_parser(pr_diff, "get-pr-diff")
    # get-pr-files
    pr_files = bitbucket.add_parser("get-pr-files", description=get_pr_files.DESCR, epilog=get_pr_files.EPILOG)
    get_pr_files.configure_parser(pr_files, "get-pr-files")
    # filter-branches
    filter_branches_parser = bitbucket.add_parser("filter-branches",
                                                  description=filter_branches.DESCR,
                                                  epilog=filter_branches.EPILOG)
    filter_branches.configure_parser(filter_branches_parser, "filter-branches")
    # filter-merged
    filter_merged_parser = bitbucket.add_parser("filter-merged",
                                                description=filter_merged.DESCR,
                                                epilog=filter_merged.EPILOG)
    filter_merged.configure_parser(filter_merged_parser, "filter-merged")
    # filter-pr
    filter_pr_parser = bitbucket.add_parser("filter-pr", description=filter_pr.DESCR, epilog=filter_pr.EPILOG)
    filter_pr.configure_parser(filter_pr_parser, "filter-pr")
    # create-branches
    create_branches_parser = bitbucket.add_parser("create-branches",
                                                  description=create_branches.DESCR,
                                                  epilog=create_branches.EPILOG)
    create_branches.configure_parser(create_branches_parser, "create-branches")
    # delete-branches
    delete_branches_parser = bitbucket.add_parser("delete-branches",
                                                  description=delete_branches.DESCR,
                                                  epilog=delete_branches.EPILOG)
    delete_branches.configure_parser(delete_branches_parser, "delete-branches")
    # create-pr
    create_pr_parser = bitbucket.add_parser("create-pr",
                                            description=create_pr.DESCR,
                                            epilog=create_pr.EPILOG)
    create_pr.configure_parser(create_pr_parser, "create-pr")
    # delete-pr
    delete_pr_parser = bitbucket.add_parser("delete-pr",
                                            description=delete_pr.DESCR,
                                            epilog=delete_pr.EPILOG)
    delete_pr.configure_parser(delete_pr_parser, "delete-pr")
    # put-pr
    put_pr_parser = bitbucket.add_parser("put-pr", description=put_pr.DESCR, epilog=put_pr.EPILOG)
    put_pr.configure_parser(put_pr_parser, "put-pr")
    # merge-pr
    merge_pr_parser = bitbucket.add_parser("merge-pr", description=merge_pr.DESCR, epilog=merge_pr.EPILOG)
    merge_pr.configure_parser(merge_pr_parser, "merge-pr")
    # create-tags
    create_tags_parser = bitbucket.add_parser("create-tags", description=create_tags.DESCR, epilog=create_tags.EPILOG)
    create_tags.configure_parser(create_tags_parser, "create-tags")


def main():
    parser = setup_parser()

    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    if COLOREDLOGS_LOG_FORMAT in os.environ is None:
        coloredlogs.install(level=nameToLevel[args.loglevel])
    else:
        coloredlogs.install(level=nameToLevel[args.loglevel], fmt=LOG_FORMAT)
    logger.debug(f'Program arguments: {args}')

    if args.version:
        v = atlassiancli.get_version()
        print(f'version={v}')
        return 0
    if args.domain is None:
        parser.print_help(sys.stderr)
        return 0
    args.func(parser, args)
    return 0


if __name__ == '__main__':
    exit(main())
