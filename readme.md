# Atlassian Command Line Interfaces, and some other useful tools
## Table of Contents
[**Introduction**](#introduction)\
[**Installation**](#installation)\
[**Disclaimer**](#disclaimer)\
[**Catalog structure**](#catalog_structure)\
[**Examples**](#examples)\
[**Design principles**](#design_principles)\
[**Development**](#development)\
[**To do**](#todo)
## Introduction <a name="introduction"></a>
### Background <a name="background"></a>
In order to manage similar changes to multiple repos the "Bitbucket Server Command Line Interface" was created. 
It was useful for mass changes to multiple repos.

Later it used to handle repetitive tagging by our Change Managers. They wanted the same powerful tools for Jira 
scripting. So the "Jira Server Command Line Inteface" was created.
### Purpose <a name="purpose"></a>
The purpose of these tools is to enhance productivity of development and maintenance of software by supplying tools 
to communicate through the command line with atlassian products bitbucket and jira.
### Goals <a name="goals"></a>
Without bragging, I can claim that these goals are met and exceeded.
#### Support multiple repo structure
It should be simple to do repetitive tasks over multiple repos. This is achieved through the pipes and filters design. 
#### Achieve high reusability
By implementing the tools as traditional filters, the tools can be recombined in infinite combinations.

The tools are implemented as python modules, and can be used in other tools easily.

The design lends itself to open source and will achieve gigantic reusability when it becomes public domain.
#### Fast
The tools sould be percieved as reasonable fast. 
#### World class documentation
The code documentation and the command line help be of excellent quality. This will help transition to external open 
source repo. 
#### Extermely high code quality
The quality of the code should be exemplary so that the myndigheten will be proud of owning such open source code.
#### Exemplary auto tests
The automatic testing of the code should be of exemplary high quality. This is a showcase of how much care myndigheten
puts on automatic testing.
## Installation <a name="installation"></a>
```
$ python -m pip install atlcli
```
### Get personal bitbucket token
See https://confluence.atlassian.com/bitbucketserver/personal-access-tokens-939515499.html
Create the token with WRITE permissions here: http://bitb.myndigheten.se/plugins/servlet/access-tokens/manage .
Store the token permanently:
```
$ setx BITBUCKET_TOKEN <your token>
```
### Get personal jira token
Create the token here: 
https://jira.myndigheten.se/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens .
Store the token permanently:
```
$ setx JIRA_TOKEN <your token>
```
### A few more environment variables
Add the url to your bitbucket server to an environment variable.
```
setx BITBUCKET_URL bitb.myndigheten.se
```
Add the url to your jira server to an environment variable.
```
setx JIRA_URL jira.myndigheten.se
```
There is a problem with python and UTF-8. This is taken care of with this setting:
```
setx PYTHONUTF8 1
```
### Verify installation
```
$ atlcli bitb get-projects | grep ASU
APPII_FUSE_ASU
ASU
```
## Disclaimer <a name="disclaimer"></a>
Do not use the "Bitbucket Server Command Line Interface" as an argument for creating a multiple repo bitb structure. 
A monorepo structure is far better. 

This is just a band-aid for a bad multiple repo design. 
## Catalog structure <a name="catalog_structure"></a>
The three catalogs bitbucketscripts, jirascrips and toolscripts contain python scripts which can be called directly 
if the repository is cloned from the bitbucket server.

The three catalogs bitbucket, jira and tools contain the heavy lifting functionality. Each of these catalogs contains 
a readme describing how to use the code through module invocation.

The catalog shared contains code common to both bitbucket and jira and tools.

The catalog atlassiancli contains the module code which uses the heavy lifting code of the three directories.

## Examples <a name="examples"></a>
This example shows details about the two tickets passed as parameters to the script.
```
$ atlcli jira get-issue AES-8313 AES-8025
652616  12201   AES-8313        2022-03-08T08:02:00.170+0100    Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se        Jiraskriptning för duplo
633257  12201   AES-8025        2022-01-27T16:04:37.377+0100    Story   Open    secret.user@myndigheten.se  None    AJA - Förbättrad felhantering
```
Here the output in the above script is fed to the get-subtasks.py script. The subtask information is prepended to the input rows.
```
$ atlcli jira get-issue AES-8313 AES-8025 | atlcli jira get-subtasks
652618  12201   AES-8314        2022-03-08T08:12:28.767+0100    Sub-task        Resolved        secret.user@myndigheten.se  secret.user@myndigheten.se  En vanlig subtask       652616  12201 AES-8313 2022-03-08T08:02:00.170+0100    Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
652835  12201   AES-8317        2022-03-08T12:23:41.970+0100    Sub-task        Closed  secret.user@myndigheten.se  None    summary 652616  12201   AES-8313        2022-03-08T08:02:00.170+0100    Story XY Utveckling pågår      secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
652866  12201   AES-8322        2022-03-08T13:53:27.110+0100    Sub-task        Closed  secret.user@myndigheten.se  None    summary 652616  12201   AES-8313        2022-03-08T08:02:00.170+0100    Story XY Utveckling pågår      secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
652940  12201   AES-8323        2022-03-08T13:55:05.237+0100    Sub-task        Closed  secret.user@myndigheten.se  None    summary 652616  12201   AES-8313        2022-03-08T08:02:00.170+0100    Story XY Utveckling pågår      secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
652896  12201   AES-8324        2022-03-08T14:54:46.657+0100    Sub-task        Resolved        secret.user@myndigheten.se  secret.user@myndigheten.se  Flytta till nytt repo   652616  12201 AES-8313 2022-03-08T08:02:00.170+0100    Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
653300  12201   AES-8327        2022-03-09T07:00:14.673+0100    Sub-task        Resolved        secret.user@myndigheten.se  secret.user@myndigheten.se  Enhetlig hantering av data      65261612201    AES-8313        2022-03-08T08:02:00.170+0100    Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
653386  12201   AES-8334        2022-03-09T12:26:44.617+0100    Sub-task        Resolved        secret.user@myndigheten.se  secret.user@myndigheten.se  Abstrahera gemensam kod 652616  12201 AES-8313 2022-03-08T08:02:00.170+0100    Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
653387  12201   AES-8335        2022-03-09T12:27:01.783+0100    Sub-task        Open    secret.user@myndigheten.se  None    Uppdatera dokumentation 652616  12201   AES-8313        2022-03-08T08:02:00.170+0100   Story   XY Utveckling pågår     secret.user@myndigheten.se  secret.user@myndigheten.se  Jiraskriptning för duplo
598210  12201   AES-7382        2021-10-27T13:19:51.810+0200    Sub-task        Open    agent.007@myndigheten.se      None    AJA - Felmeddelande vid basexception i backend <utv>    633257  12201   AES-8025       2022-01-27T16:04:37.377+0100    Story   Open    secret.user@myndigheten.se  None    AJA - Förbättrad felhantering
620837  12201   AES-7806        2021-12-16T16:54:04.267+0100    Sub-task        Open    secret.user@myndigheten.se  None    Testa felhanteringen i klienten 633257  12201   AES-8025        2022-01-27T16:04:37.377+0100   Story   Open    secret.user@myndigheten.se  None    AJA - Förbättrad felhantering

```

## Design principles <a name="design_principles"></a>
### Unix pipes and filters
The tools are meant to be used and reused with the unix pipe system. Output from a script is used by the next script as input. The scripts are filters.
### Shell integration
Shell tools should be used when possible. For example, creating subdirectories for jira projects are done using a shell script. There is no need for at python script here for this purpose.
### Table data
Output is organized as columns and rows. Much inspired from relational database principles. 
### Stack organization of output columns
When a script adds data to its input row, the new data is prepended to the input line. The reason is increased reusability. If for example we would like to write a script to show epic information, this can be used independent of how we created the input data.
## Development <a name="development"></a>
### Install python3
Install python 3 and verify python version
```
$ python --version
Python 3.11.2
```
### Clone this repo and set PATH
I am using ssh keys stored in the Bitbucket Server. 
* Clone this repo
```
$ cd /c/SecretPath/repos
$ mkdir git
$ cd git
$ mkdir IOS
$ cd IOS
$ git clone ssh://git@bitb.myndigheten.se:7999/ios/atlassian-cli.git
```
* Add the catalogs to path

Unfortunately it is impossible to add to the user path with a command. Follow these instructions to add a catalog to the
path variable: 
https://stackoverflow.com/questions/44272416/how-to-add-a-folder-to-path-environment-variable-in-windows-10-with-screensho
Add these catalogs
```
C:\SecretPath\repo\git\IOS\atlassian-cli\bitbucketscripts
C:\SecretPath\repo\git\IOS\atlassian-cli\jirascripts
C:\SecretPath\repo\git\IOS\atlassian-cli\toolscripts
```
to the list of catalogs.
* Restart bash
* Verify installation and path
```
$ which get-repos.py
/c/SecretPath/repos/git/IOS/bitbucketscripts/get-repos.py
```
### Make sure you have access to nexus
Setup our account in nexus. Log in using the web gui
### Set environments variables for twine
Check your environment when done
```
$ printenv | grep TWINE
TWINE_PASSWORD=**********
TWINE_USERNAME=*********
```
### Build
```
$ python -m build -n
```
### Install .whl file
```
$ python -m pip install dist/atlcli-<version>-py3-none-any.whl
```

### Upload to nexus

```
$ python -m twine upload --repository-url https://python.repo.myndigheten.se/repository/production/ dist/atlcli-<version>-py3-none-any.whl
```
### Unit tests
The tests for bitbucket are in catalog bitbucket-tests. The test data is created by running the scripts with --trace option. The trace files are used by a test server mimicking the bitbucket server. These tests are regression tests.
## To do <a name="todo"></a>
### Anonymize
There are three files which need to be altered/removed before move to open source repo. Search for "Needs to be anonymized".
### Unit tests
Th