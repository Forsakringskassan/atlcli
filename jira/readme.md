# Jira Server Command Line Interface 
## Background
My CM wanted to be able to script subtask creation. Of course, he got it
## Short description of the scripts
### atlcli jira get-projects
Retrieves all jira projects from the Jira Server.
### atlcli jira get-boards
Retrieves all boards from the Jira Server.
### atlcli jira get-issues
For each board in input, lists all issues. Avoid this function because of
horrible performance.
## atlcli jira get-issue
Retrieves named issues from the jira server.
## atlcli jira get-subtasks
For each issue in input, lists all subtasks.
## atlcli jira create-subtask
Creates a jira subtask.
