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
    addr = quote("/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}".format(project, repo, id))
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
    addr = quote("/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/merge".format(project, repo, id))
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
