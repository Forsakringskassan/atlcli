"""
The purpose of this module is to hold reusable code. It contains only one function named as the file.
"""

import sys
import os
import json

from shared import connection
from shared.output import print_error
from shared.trace import trace_request, trace_response
from shared.quote import quote

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

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
            addr = quote(request.format(project, repo, part, page))
            logger.debug(addr)
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
                return results

    return results
