"""
The purpose of this module is to hold reusable code. It contains only one function named as the file.
"""
import sys
import os
import json

from shared import connection
from shared.output import print_error, print_debug
from shared.trace import trace_request, trace_response
from shared.version import Version
from shared.quote import quote

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def search_branch_or_tag(env, project, repo, line, branch_or_tag, patterns, default, out_displ_id, invert,
                         script_name, logger):
    """Searches for branch and/or tag in the repo belonging to the project using regular expressions.

    This function is useful when you want to find branches or tags given a regular expression given as a
    command line parameter.

    If the regular expression pattern list is empty, all branches/tags are returned.

    For a project/repo to be included in output all searched for branches/tags must be found.

    If a pattern matches multiple branches/tags, the 'largest' branch/tag is chosen. The comparison is
    semantic version aware.

    Parameters
    ----------
    env : Environment
        properties from environment or command line
    project : str
        The symbolic name of the bitbucket project to search.
    repo : str
        The name of the bitbucket repo to search.
    line : str
        The input line trimmed from carriage return and line feed
    branch_or_tag : str
        "branches" if you want to search branches. "tags" if you want to search tags. "branchestags" if you want to
        search both branches and tags. Other combinations works as well, you are welcome to peek.
    patterns : list
        A list of compiled regular expressions to search for.
    out_displ_id : bool
        If true, display id is returned. Otherwise fully qualified name.
    invert : bool
        If true, the search is inverted.
    script_name : str
        The name of the calling script.
    logger : logging.Logger
        The logger to use.
    Returns
    -------
    list
        A list of output lines
    """
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp181
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp323
    # Result is the same for both these calls.
    request = "/rest/api/1.0/projects/{}/repos/{}/{}?start={}"
    result = []
    page = 0
    token_header = "Bearer {}".format(env.token)
    matches = []
    results = []
    for pattern in patterns:
        # print(pattern)
        matches.append(Version(''))
        results.append('')
    for part in ['branches', 'tags']:
        is_last_page = False
        if part not in branch_or_tag:
            continue
        while not is_last_page:
            addr = quote(request.format(project, repo, part, page))
            logger.debug(addr)
            # print(addr)
            conn = connection.create(env)
            h = {"User-Agent": "Python-3.7.1", "Accept": "application/json", "Authorization": token_header}
            verb = "GET"
            uuid = trace_request(script_name, verb, addr) if env.trace else None
            conn.request(verb, addr, headers=h)
            response = conn.getresponse()
            if response.status == 200:
                data = json.load(response)
                env.trace and trace_response(uuid, script_name, verb, addr, response.status, data)
                for value in data['values']:
                    if len(patterns) == 0:
                        id = value['displayId'] if out_displ_id else value['id']
                        if default is None or not default:
                            result.append("{}{}{}".format(id, env.sep, line))
                        elif default:
                            is_default = value['isDefault']
                            if is_default:
                                result.append("{}{}{}".format(id, env.sep, line))
                    else:
                        display_id = value['displayId']
                        for i in range(0, len(patterns)):
                            pattern = patterns[i]
                            if pattern.fullmatch(display_id) is not None:
                                version = Version(display_id)
                                if version > matches[i]:
                                    matches[i] = version
                                    results[i] = display_id if out_displ_id else value['id']
                is_last_page = data['isLastPage']
                if not is_last_page:
                    page = data['nextPageStart']
            else:
                print_error(env, addr, response, script_name)
                return result

    if len(patterns) != 0:
        missing_branch = False
        existing_branch = False
        for i in range(0, len(matches)):
            if str(matches[i]) == '':
                missing_branch = True
            else:
                existing_branch = True
        if invert:
            if not existing_branch:
                result.append(line)
        else:
            if not missing_branch:
                output_line = None
                print_debug(env, results)
                for r in results:
                    if output_line is None:
                        output_line = "{}".format(r)
                    else:
                        output_line = "{}{}{}".format(output_line, env.sep, r)
                output_line = "{}{}{}".format(output_line, env.sep, line)
                result.append(output_line)
    return result
