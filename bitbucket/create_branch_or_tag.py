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
    addr = quote("/rest/api/1.0/projects/{}/repos/{}/{}".format(project, repo, branch_or_tag))
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
        return result

    return result
