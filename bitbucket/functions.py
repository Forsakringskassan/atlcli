"""
The purpose of this module is to hold reusable code. It contains only functions.
"""
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from shared.version import Version
from shared import connection
from shared.environment import Environment
from shared.trace import trace_response, trace_request
from shared.output import print_error, print_debug


def search_branch_or_tag(env, project, repo, line, branch_or_tag, patterns, default, out_displ_id, invert, script_name):
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
            addr = request.format(project, repo, part, page)
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
                return None

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


def get_branch_or_tag(env, project, repo, branch_or_tag, names, script_name):
    """Retrieves a list of named records from the bitbucket server.

    Use this function when the names are retrieved from input. There is no need to search when the ids are retrieved
    from input. There should be at most one matching branch or tag.
    Parameters
    ----------
    env : Environment
        properties from environment or command line
    project : str
        The symbolic name of the bitbucket project to search.
    repo : str
        The name of the bitbucket repo to search.
    branch_or_tag : str
        "branches" if you want to retrieve branches. "tags" if you want to get tags. "branchestags" if you want to
        get both branches and tags. Other combinations works as well, you are welcome to peek.
    names : list
        A list of branch and/or tag names to retrieve from the server.
    script_name : str
        The name of the calling script.
    Returns
    -------
    list
        A list of retrieved records. One record per name in input parameter names. If the name is not
        found, None is returned in the corresponding position
    """
    token_header = "Bearer {}".format(env.token)
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp181
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp323
    # Result is the same for both these calls.
    request = "/rest/api/1.0/projects/{}/repos/{}/{}?start={}"
    results = []
    for name in names:
        results.append(None)
    for part in ['branches', 'tags']:
        if not part in branch_or_tag:
            continue
        page = 0
        is_last_page = False

        while not is_last_page:
            addr = request.format(project, repo, part, page)
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
                all_matches = True
                for value in data['values']:
                    display_id = value['displayId']
                    id = value['id']
                    for i in range(0, len(names)):
                        name = names[i]
                        if name == display_id or name == id:
                            results[i] = value
                        elif results[i] is None:
                            all_matches = False
                is_last_page = all_matches or data['isLastPage']
                if not is_last_page:
                    page = data['nextPageStart']
            else:
                print_error(env, addr, response, script_name)
                return None

    return results


def create_branch_or_tag(env, project, repo, branch_or_tag, commit, name, message, script_name):
    """ Creates a branch or a tag.
    Parameters
    ----------
    env : Environment
        properties from environment or command line
    project : str
        The symbolic name of the bitbucket project to search.
    repo : str
        The name of the bitbucket repo to search.
    branch_or_tag : str
        "branches" if you want to retrieve branches. "tags" if you want to get tags. "branchestags" if you want to
        get both branches and tags. Other combinations works as well, you are welcome to peek.
    commit : str
        The commit id used to create the branch or tag.
    name : str
        The name of the created branch or tag.
    message : str
        Message associated with branch or tag.
    script_name : str
        The name of the calling script.
    """
    token_header = "Bearer {}".format(env.token)
    result = []
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp182
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp322
    # Body is same for both these calls
    addr = "/rest/api/1.0/projects/{}/repos/{}/{}".format(project, repo, branch_or_tag)
    conn = connection.create(env)
    h = {"User-Agent": env.version,
         "Content-Type": "application/json",
         "Accept": "application/json",
         "Authorization": token_header}
    body = {
        'name': name,
        'startPoint': commit,
        'message': message
    }
    # print(json.dumps(body))
    verb = "POST"
    uuid = trace_request(script_name, verb, addr, body) if env.trace else None
    conn.request(verb, addr, body=json.dumps(body), headers=h)
    response = conn.getresponse()
    if response.status == 200:
        data = json.load(response)
        env.trace and trace_response(uuid, script_name, verb, addr, response.status, data)
        result.append("{}{}{}{}{}".format(data['id'], env.sep, repo, env.sep, project))
    else:
        print_error(env, addr, response, script_name)
        return None

    return result


def get_pr_and_merge(env, project, repo, id, script_name):
    """ Retrieves pull request data and merge data for pull request.
    Parameters
    ----------
    env : Environment
        properties from environment or command line
    project : str
        The symbolic name of the bitbucket project to search.
    repo : str
        The name of the bitbucket repo to search.
    id : str
        The pull request id.
    script_name : str
        The name of the calling script.
    Returns
    -------
    tuple
        The first object is the pull request record. The second is the merge data record.
    """
    token_header = "Bearer {}".format(env.token)
    pr_data = None
    merge_data = None
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp258
    # https://docs.atlassian.com/bitbucket-server/rest/6.5.1/bitbucket-rest.html#idp266
    addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}".format(project, repo, id)
    # print(addr)
    conn = connection.create(env)
    h = {"User-Agent": "Python-3.7.1", "Accept": "application/json", "Authorization": token_header}
    verb = "GET"
    uuid = trace_request(script_name, verb, addr) if env.trace else None
    conn.request(verb, addr, headers=h)
    response = conn.getresponse()
    if response.status == 200:
        pr_data = json.load(response)
        env.trace and trace_response(uuid, script_name, verb, addr, response.status, pr_data)
        # print(data)
    else:
        print_error(env, addr, response, script_name)
        return None, None

    if pr_data['state'] == 'MERGED' or pr_data['state'] == 'DECLINED':
        return pr_data, None
    addr = "/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/merge".format(project, repo, id)
    # print(addr)
    uuid = trace_request(script_name, verb, addr) if env.trace else None
    conn = connection.create(env)
    conn.request(verb, addr, headers=h)
    response = conn.getresponse()
    if response.status == 200:
        merge_data = json.load(response)
        env.trace and trace_response(uuid, script_name, verb, addr, response.status, merge_data)
        # print(data)
    else:
        print_error(env, addr, response, script_name)
        merge_data = None

    return pr_data, merge_data


def decode(line, coding):
    """
    Decodes a line according to the coding
    :param line: The line to decode
    :param coding: The encoding to use
    :return: a successfully decoded line and None, or None and the caught UnicodeDecodeError
    """
    try:
        return line.decode(coding).rstrip(), None
    except UnicodeDecodeError as e:
        return None, e


