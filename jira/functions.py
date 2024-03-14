"""
The purpose of this module is to hold reusable code. It contains only functions.
"""
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from shared import trace as trace
from shared import connection

def extract_issue_data(issue):
    issue_id = issue['id']
    key = issue['key']
    fields = issue['fields']
    reporter = fields['reporter']
    reporterName = reporter['emailAddress'] if reporter else None
    creator = fields['creator']
    creatorName = creator['emailAddress'] if creator else "None"
    origin = reporterName if reporterName else creatorName
    assignee = fields['assignee']
    assigneeName = assignee['emailAddress'] if assignee else "None"
    status = fields['status']['name']
    issue_type = fields['issuetype']['name']
    created = fields['created']
    summary = fields['summary']
    project = fields['project']['id']
    return issue_id, project, key, assigneeName, created, origin, status, issue_type, summary


def get_subtask(env, line, subtask_id):
    token_header = "Bearer {}".format(env.token)
    conn = connection.create(env)
    h = {"User-Agent": env.version, "Accept": "application/json", "Authorization": token_header}
    verb = "GET"
    subtask_addr = "/rest/api/2/issue/{}".format(subtask_id)
    subtask_uuid = trace.trace_request(env.script, "GET", subtask_addr) if env.trace else None
    conn.request("GET", subtask_addr, headers=h)
    subtask_response = conn.getresponse()
    if subtask_response.status == 200:
        subtask_data = json.load(subtask_response)
        subtask_id, project, issue_key, assignee, created, origin, status, issue_type, summary = \
            extract_issue_data(subtask_data)
        subtask_line = "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(subtask_id, env.sep, project, env.sep, issue_key,
                                                                       env.sep, created, env.sep, issue_type, env.sep,
                                                                       status, env.sep, origin, env.sep, assignee,
                                                                       env.sep,
                                                                       summary, env.sep, line)
    else:
        subtask_line = None
    return subtask_line