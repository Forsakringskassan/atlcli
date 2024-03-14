# Bitbucket Server Command Line Interface 
## Background
Our subsystem source code is stored in ~250 git repos hosted on a Bitbucket Server.

We need to be able to do repetitive things in all those repos. This is accomplished by a set of 
python scripts designed as shell filters. Output from one script is piped as input to the next. 

This design also allows us to use standard unix filters. Bash integration is quite simple.

A small snack:
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | \
atlcli bitb get-file-names -n '^pyproject.toml' | atlcli bitb get-file-urls | \
atlcli bitb get-file-content lines 'version.*' | atlcli tool select-columns 1 5
version = "1.0.0"       atlassian-cli
version = {attr = "postgresqlpatches.__version__"}      python-postgresql-patches
version = "0.3.0"       spdb-tools
```
This is how we find the version of all our python projects.
## Short description of the scripts
### atlcli bitb get-users
Retrieves all users from the Bitbucket Server.   
### atlcli bitb get-projects
Retrieves all projects from the Bitbucket Server.   
### atlcli bitb get-repos  
For each project in input, lists all repos.
### atlcli bitb get-clone-urls
Adds the clone url for each project and repo name in input.
### atlcli bitb get-branches
For each project and repo name in input, lists or searches branch names.
### atlcli bitb get-tags
For each project and repo name in input, lists or searches tag names. Works
exactly as atlcli bitb get-branches but for tags instead.
### atlcli bitb get-branches-or-tags
For each project and repo name in input, lists or searches branch and tag
names.
### atlcli bitb get-commits
For each project, repo and branch/tag in input, adds latest commit id.
### atlcli bitb get-commit-details
Adds commit details for each project, repo, branch and commit id in input.
### atlcli bitb create-branches
Creates a new branch for each project, repo and commit id in input.
### atlcli bitb create-tags
Creates a tag for each project, repo and commit id in input.
### atlcli bitb delete-branches
Deletes a branch for each project, repo and branch name in input.
### atlcli bitb filter-branches
For each project, repo and branch names in input, filters existing branches.
### atlcli bitb filter-merged
For each project, repo and two branch names in input, filters merged branch
pairs.
### atlcli bitb get-file-names
Lists or searches file names for each project, repo and branch in input.
### atlcli bitb get-file-details
For each file in input, adds last modified date, commiter, commit message and commit id.
### atlcli bitb get-file-urls
Lists download url for each project, repo, branch and file name in input.
### atlcli bitb get-file-content
Downloads files and searches file contents. Matching rows are output.
### atlcli bitb create-pr
Creates a pull request for each project, repo and two branch names in input.
### atlcli bitb get-pr
For each input line, prints outgoing branch, incoming branch and pull request
id.
### atlcli bitb get-pr-files
Adds affected file names of a pull request for each project, repo, branch
names and pull request id in input.
### atlcli bitb get-pr-details
Adds pull request details for each project, repo, branch
name and pull request id in input.
### atlcli bitb filter-pr
For each project, repo, branch names and pull request id in input, filter only
those pull requests which can be merged and contains changes.
### atlcli bitb put-pr
Changes pull request state for each project, repo and pull request id in
input.
### atlcli bitb merge-pr
For each project, repo, branch names and pull request id in input, the pull
request is merged if mergeable.
### atlcli bitb delete-pr
For each project, repo, branch names and pull request id in input, the pull
request is deleted.

## Flowchart
```
get-users
get-projects   
   get-repos   
      get-clone-urls
      get-branches | get-tags | get-branches-or-tags
        get-commits
           get-commit-details
           create-branches
           create-tags
        delete-branches
        filter-branches
        filter-merged
        get-file-names
           get-file-urls
              get-file-content
           get-file-details
        create-pr
        get-pr
      get-pr
        get-pr-files
        get-pr-details
        get-pr-diff
        filter-pr
        put-pr
        merge-pr
        delete-pr
```
## atlcli bitb get-users
```
$ atlcli bitb get-users -h
usage: atlcli bitb get-users [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                    [-a SEPARATOR] [-f FILTER]
                    [{all,id,name,displayName,emailAddress} ...]

Retrieves all users from the Bitbucket Server.

positional arguments:
  {all,id,name,displayName,emailAddress}
                        Display fields (default: all)

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -f FILTER, --filter FILTER
                        Filters on user name or email address containing the
                        filter (default: None)

Each user is printed to a separate line.


```
### List myself
```
$ atlcli bitb get-users -f Author | grep 392
392     66115350        Secret Author       secret.author@myndigheten.se

```

## atlcli bitb get-projects
```
$ atlcli bitb get-projects -h
usage: atlcli bitb get-projects [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                       [-f {KEY,NAME,BOTH}]

Retrieves all projects from the Bitbucket Server.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -f {KEY,NAME,BOTH}, --format {KEY,NAME,BOTH}
                        Output format. KEY means project key, NAME is project
                        name, BOTH means key:name (default: KEY)

Each project is printed to a separate line. Pipe output to get-repos.

```
### List all projects matching a regular expression
```
$ atlcli bitb get-projects -n 'IOS.*'
IOS
IOS_OS_CHASSI

```
### Create a directory for each project
```
$ atlcli bitb get-projects -n 'IOS.*' | dos2unix | while IFS= read -r line; do mkdir $line; done
$ ls
IOS/  IOS_OS_CHASSI/

```
## atlcli bitb get-repos
```
$ atlcli bitb get-repos-h
usage: atlcli bitb get-repos[-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                    [-w WORKERS] [-l FILE] [-a SEPARATOR]
                    [-s {AVAILABLE,INITIALISING,INITIALISATION_FAILED}] [-c]

For each project in input, lists all repos.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -s {AVAILABLE,INITIALISING,INITIALISATION_FAILED}, --state {AVAILABLE,INITIALISING,INITIALISATION_FAILED}
                        Repository state. (default: AVAILABLE)
  -c, --count           Output number of repos instead of names (default:
                        False)

Input is each project name on a separate line. Output is repo name followed by
project name, separated by tab. Pipe output to atlcli bitb get-branches or atlcli bitb get-tags
or get-branchesor-tags or get-clone-urls or get-pr.

```
### List all repos for a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos
atlassian-cli   IOS
chassi  IOS
xye-processfasad        IOS
xye-processmotor        IOS
xy-gradle-config        IOS
hundbidrag-backend      IOS
lok-obs IOS
migrera_mappstruktur_till_git   IOS
process4j       IOS
python-postgresql-patches       IOS
readme  IOS
spdb-tools      IOS
spring-clients  IOS


```
### Checks status for some checked out repos
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | dos2unix | \
while IFS=$'\t' read repo proj; do pushd $proj/$repo; git status; popd; done
/c/SecretPath/repo/git/IOS/test/IOS/atlassian-cli /c/SecretPath/repo/git/IOS/test
On branch master
Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean
/c/SecretPath/repo/git/IOS/test
/c/SecretPath/repo/git/IOS/test/IOS/chassi /c/SecretPath/repo/git/IOS/test
On branch develop
Your branch is up to date with 'origin/develop'.

```
### Errorhandling
Sometimes you want to abort the whole pipe when there is an error. A couple of bash commands are helpful. 
```
$ set --help | grep -- '-e'
      -e  Exit immediately if a command exits with a non-zero status.
              errexit      same as -e
```
'set -e' terminates on error.
```
$ set --help | grep -- '-o'
set: set [-abefhkmnptuvxBCHP] [-o option-name] [--] [arg ...]
      -o option-name
$ set --help | grep -A 2 pipefail
              pipefail     the return value of a pipeline is the status of
                           the last command to exit with a non-zero status,
                           or zero if no command exited with a non-zero status
```
'set -o pipefail' terminates pipe on error.

If you enter these at the prompt, your shell will close at first error. You will not be able to see the error printout.
Therefor we issue them in a subshell.

Enclosing parenthesis creates a subshell.
### Builds all python projects
```
$ (set -e && set -o pipefail && atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | dos2unix | \
while IFS=$'\t' read repo proj; do pushd $proj/$repo; [[ -f pyproject.toml ]] && python -m build -n; popd; done)
/c/SecretPath/repo/git/IOS/test/IOS/atlassian-cli /c/SecretPath/repo/git/IOS/test
* Getting build dependencies for sdist...
C:\SecretPath\Python311-64\Lib\site-packages\setuptools\config\pyprojecttoml.py:108: _BetaConfiguration: Support for `[tool.setuptools]` in `pyproject.toml` is still *beta*.
  warnings.warn(msg, _BetaConfiguration)
running egg_info
creating atlcli.egg-info
writing atlcli.egg-info\PKG-INFO
writing dependency_links to atlcli.egg-info\dependency_links.txt
writing entry points to atlcli.egg-info\entry_points.txt
writing top-level names to atlcli.egg-info\top_level.txt
writing manifest file 'atlcli.egg-info\SOURCES.txt'
error: package directory 'atlassianshared' does not exist

ERROR Backend subprocess exited when trying to invoke get_requires_for_build_sdist

```

## atlcli bitb get-clone-urls
```
$ atlcli bitb get-clone-urls -h
usage: atlcli bitb get-clone-urls [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                         [-w WORKERS] [-l FILE] [-a SEPARATOR] [-e {ssh,http}]

For each repo in input adds the clone url.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -e {ssh,http}, --type {ssh,http}
                        Type of url to get (default: ssh)

Input is repo name followed project name. Output is the clone url followed by
input line.


```
### List the clone urls for each repo in a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-clone-urls
ssh://git@secret.git.repo:7999/ios/atlassian-cli.git atlassian-cli   IOS
ssh://git@secret.git.repo:7999/ios/chassi.git        chassi  IOS
ssh://git@secret.git.repo:7999/ios/xye-processfasad.git      xye-processfasad        IOS
ssh://git@secret.git.repo:7999/ios/xye-processmotor-publication.git  xye-processmotor-publication    IOS
ssh://git@secret.git.repo:7999/ios/xye-processmotor-src.git  xye-processmotor-src    IOS
ssh://git@secret.git.repo:7999/ios/xy-gradle-config.git      xy-gradle-config        IOS
ssh://git@secret.git.repo:7999/ios/hundbidrag-backend.git    hundbidrag-backend      IOS
ssh://git@secret.git.repo:7999/ios/lok-obs.git       lok-obs IOS
ssh://git@secret.git.repo:7999/ios/migrera_mappstruktur_till_git.git migrera_mappstruktur_till_git   IOS
ssh://git@secret.git.repo:7999/ios/process4j.git     process4j       IOS
ssh://git@secret.git.repo:7999/ios/python-postgresql-patches.git     python-postgresql-patches       IOS
ssh://git@secret.git.repo:7999/ios/readme.git        readme  IOS
ssh://git@secret.git.repo:7999/ios/spdb-tools.git    spdb-tools      IOS
ssh://git@secret.git.repo:7999/ios/spring-clients.git        spring-clients  IOS

```
### Clones all repos in a set of projects
```
$ (set -e &&  set -o pipefail && atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | \
atlcli bitb get-clone-urls | dos2unix | \
while IFS=$'\t' read url repo proj; do pushd $proj; git clone -c core.longpaths=true $url; popd; done)
$ ls *
IOS:
atlassian-cli/  xy-gradle-config/  xye-processmotor-publication/  hundbidrag-backend/  migrera_mappstruktur_till_git/  python-postgresql-patches/  spdb-tools/
chassi/         xye-processfasad/  xye-processmotor-src/          lok-obs/             process4j/                      readme/                     spring-clients/

IOS_OS_CHASSI:
xy-egress-proxy-template/    xy-ingress-proxy-template/  xy-quarkus-template/  xy-vue-template/  hub-xye-backend/  hub-xye-egress-proxy/  hub-xye-frontend---backup/  hub-xye-simulator/
xy-helm-deployment-library/  xy-quarkus-app-template/    xy-vue-app-template/  hub-ark-config/   hub-xye-config/   hub-xye-frontend/      hub-xye-ingress-proxy/      readme/

```
## atlcli bitb get-branches
```
$ atlcli bitb get-branches --help
usage: atlcli bitb get-branches [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                       [-w WORKERS] [-l FILE] [-a SEPARATOR]
                       [-n NAMES [NAMES ...] | -f] [-d] [-i]

For each repo in input, lists or searches branch names.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -n NAMES [NAMES ...], --names NAMES [NAMES ...]
                        Space separated list of regular expressions defining
                        branches. The display name us used here as it is
                        shorter. If no branch name is given all branches are
                        returned, each on a separate line. (default: None)
  -f, --default         Output default branch. Cannot be used with -n switch.
                        (default: False)
  -d, --displayid       Output displayid instead of id, useful for bash
                        integration (default: False)
  -i, --invert          Invert logic. Only repos with all listed branches
                        missing are included in output. Only makes sense with
                        -n switch (default: False)

Input is repo (first column) and project (second column). Other columns are
ignored. Branch fully qualified names are used in the output, unless switch -d
is used. If switch -n is defined only those repos with all matching branches
are included in output. Each output line consists of all matching branches, in
separate columns, followed by input line. If there are multiple branches
matching a branch pattern, the largest branch name is used. This can be handy
to find current release branch for example. Branch name comparison is semantic
version aware. The branch names are split using full stop, and each part is
compared. A longer string is "larger" than a short string in a versionized
name. If there are no full stops in the name, traditional string comparison is
used. If switch -n is not defined, all branches are included in output, each
branch on a separate line. Pipe output to atlcli bitb get-commits or atlcli bitb delete-branches
or atlcli bitb filter-branches or atlcli bitb filter-merged or atlcli bitb get-file-names or atlcli bitb create-pr
or atlcli bitb get-pr.

```
### List all develop branches in a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop
refs/heads/develop      atlassian-cli   IOS
refs/heads/develop      chassi  IOS
refs/heads/develop      xye-processfasad        IOS
refs/heads/develop      xye-processmotor-publication    IOS
refs/heads/develop      xye-processmotor-src    IOS
refs/heads/develop      hundbidrag-backend      IOS
refs/heads/develop      process4j       IOS
refs/heads/develop      python-postgresql-patches       IOS
refs/heads/develop      spdb-tools      IOS
refs/heads/develop      spring-clients  IOS

```
### List all branches in a repo
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | grep atlassian | atlcli bitb get-branches
refs/heads/feature/anonymisera  atlassian-cli   IOS
refs/heads/develop      atlassian-cli   IOS
refs/heads/dummy/merge2 atlassian-cli   IOS
refs/heads/feature/test2        atlassian-cli   IOS
refs/heads/master       atlassian-cli   IOS
refs/heads/feature/testa-ny-groovy      atlassian-cli   IOS


```
### List all repos in a project with current release branch
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n 'release/.*'
refs/heads/release/1.0.0        process4j       IOS

```
### Lists all repos in a project having both develop and master branches using display name in output
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop master -d
develop master  atlassian-cli   IOS
develop master  chassi  IOS
develop master  xye-processfasad        IOS
develop master  hundbidrag-backend      IOS
develop master  process4j       IOS
develop master  python-postgresql-patches       IOS
develop master  spdb-tools      IOS

```
### Lists all repos in a project having both develop and master branches using qualified names in output
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop master
refs/heads/develop      refs/heads/master       atlassian-cli   IOS
refs/heads/develop      refs/heads/master       chassi  IOS
refs/heads/develop      refs/heads/master       xye-processfasad        IOS
refs/heads/develop      refs/heads/master       hundbidrag-backend      IOS
refs/heads/develop      refs/heads/master       process4j       IOS
refs/heads/develop      refs/heads/master       python-postgresql-patches       IOS
refs/heads/develop      refs/heads/master       spdb-tools      IOS

```
### Lists the master branch for all repos missing develop branch
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-branches -i -n develop | atlcli bitb get-branches -n master
refs/heads/master       xy-gradle-config        IOS
refs/heads/master       lok-obs IOS
refs/heads/master       migrera_mappstruktur_till_git   IOS
refs/heads/master       readme  IOS
refs/heads/master       xy-egress-proxy-template        IOS_OS_CHASSI
refs/heads/master       xy-ingress-proxy-template       IOS_OS_CHASSI
refs/heads/master       xy-vue-app-template     IOS_OS_CHASSI
refs/heads/master       xy-vue-template IOS_OS_CHASSI
refs/heads/master       hub-xye-frontend        IOS_OS_CHASSI
```
### Check out develop branch and pull, for all repos in a set of projects
```
$ (set -e && set -o pipefail && \
atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop -d | dos2unix | \
while IFS=$'\t' read branch repo proj; do pushd $proj/$repo; pwd; git checkout $branch; git pull; popd; done)
/c/SecretPath/repo/git/IOS/test/IOS/atlassian-cli /c/SecretPath/repo/git/IOS/test
/c/SecretPath/repo/git/IOS/test/IOS/atlassian-cli
Switched to a new branch 'develop'
branch 'develop' set up to track 'origin/develop'.
Already up to date.

```

### List all repos missing both develop and master branches
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-branches -i -n develop master
xy-helm-deployment-library      IOS_OS_CHASSI
readme  IOS_OS_CHASSI


```
## atlcli bitb get-tags
```
$ atlcli bitb get-tags --help
usage: atlcli bitb get-tags [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                   [-w WORKERS] [-l FILE] [-a SEPARATOR]
                   [-n NAMES [NAMES ...]] [-d] [-i]

For each repo in input, lists or searches tag names. Works exactly as get-
branches but for tags instead.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -n NAMES [NAMES ...], --names NAMES [NAMES ...]
                        Space separated list of regular expressions defining
                        tags. The display name us used here as it is shorter.
                        If no tag name is given all tags are returned, each on
                        a separate line. (default: None)
  -d, --displayid       Output displayid instead of id, useful for bash
                        integration (default: False)
  -i, --invert          Invert logic. Only repos with all listed tags missing
                        are included in output. Only makes sense with -n
                        switch (default: False)

Reads repo (first column) and project (second column) from input. Other
columns are ignored. Tag
fully qualified names are used in the output, unless switch -d is used. If
switch -n is defined only those repos with all matching tags are included in
output. Each output line consists of all matching tags, in separate columns,
followed by input line. If there are multiple tags matching a tag pattern, the
largest tag name is used. Tag name comparison is semantic version aware. The
tag names are split using full stop, and each part is compared. A longer
string is "larger" than a short string in a versionized name. If there are no
full stops in the name, traditional string comparison is used. If switch -n is
not defined, all tags are included in output, each tag in a separate line.
Pipe output to atlcli bitb get-commits or atlcli bitb filter-merged or atlcli bitb get-file-names.

```
### Search for a tag name in a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-tags -n v0.14.0
refs/tags/v0.14.0       process4j       IOS

```
### Search for a tag name in a project using a regular expression
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-tags -n '0\.2\.0.*'
refs/tags/0.2.0+20230510140112  python-postgresql-patches       IOS
```

## atlcli bitb get-commits
```
$ atlcli bitb get-commits --help
usage: atlcli bitb get-commits [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                      [-w WORKERS] [-l FILE] [-a SEPARATOR]

For each branch in input, prints latest commit id.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Input is branch (first column), repo (second column) and project (third
column). Output is commit id followed by input line.
```
### Finds latest commits for branch develop for all repos in a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | atlcli bitb get-commits
22cb5542e296b57653146999f43c7b100cc9983c        refs/heads/develop      atlassian-cli   IOS
6fe9a13a2bbdbf1dec9824bce7d76efd12ab1ccf        refs/heads/develop      chassi  IOS
8ccf17b3134c3257838f53f9752a0974600f9cd6        refs/heads/develop      xye-processfasad        IOS
3845caa90f6ee4ea28012c5a5fa3fc9b58406ab0        refs/heads/develop      xye-processmotor-publication    IOS
00001b21952ccd132740ad464b20da85d6478cab        refs/heads/develop      xye-processmotor-src    IOS
4c9309436b02ea33374a5d2efdc112b2ee1e8538        refs/heads/develop      hundbidrag-backend      IOS
993e3a45715c623c4e2ad2d2c3ccfb0b8ecf255f        refs/heads/develop      process4j       IOS
4726d57f1d52a64044622168509ec0eca0b5d829        refs/heads/develop      python-postgresql-patches       IOS
d233234d0e3e5cf4c59d79852803138a7c4df4a7        refs/heads/develop      spdb-tools      IOS
f345cfffa2a083f99d1f489dbf42f70d15ad26b2        refs/heads/develop      spring-clients  IOS

```
## atlcli bitb get-commit-details
```
$ atlcli bitb get-commit-details --help
usage: atlcli bitb get-commit-details [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                             [-w WORKERS] [-l FILE] [-a SEPARATOR]

Adds commit details for each commit id in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Input is commit id (first column), repo (third column) and project (fourth
column). Output is input line and added commit information in form of json.
```
### Gets the commit details for a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | atlcli bitb get-commits | atlcli bitb get-commit-details
{"created": "2023-05-17T17:57:11.000000", "committer": "66115350", "message": "Testar"} 22cb5542e296b57653146999f43c7b100cc9983c        refs/heads/develop      atlassian-cli   IOS
{"created": "2023-04-27T15:13:04.000000", "committer": "66122872", "message": "Doc"}    6fe9a13a2bbdbf1dec9824bce7d76efd12ab1ccf        refs/heads/develop      chassi  IOS
{"created": "2023-05-15T08:55:29.000000", "committer": "66121770", "message": "Initial commit"} 8ccf17b3134c3257838f53f9752a0974600f9cd6        refs/heads/develop      xye-processfasad        IOS
{"created": "2023-06-09T14:44:17.000000", "committer": "66128462", "message": "alla \u00e4ndringar i helper.tpl kom inte med av n\u00e5gon anledning"}  3845caa90f6ee4ea28012c5a5fa3fc9b58406ab0        refs/heads/develop      xye-processmotor-publication       IOS
{"created": "2023-06-09T14:09:57.000000", "committer": "66128462", "message": "flyttade publikations filer till separat repo"}  00001b21952ccd132740ad464b20da85d6478cab        refs/heads/develop      xye-processmotor-src    IOS
{"created": "2023-04-11T10:36:36.000000", "committer": "66119584", "message": "feat: adding cypress and cucumber (refs: BETA-194)"}     4c9309436b02ea33374a5d2efdc112b2ee1e8538        refs/heads/develop      hundbidrag-backend      IOS
{"created": "2023-03-31T10:13:16.000000", "committer": "66118865", "message": "enhanced tooling"}       993e3a45715c623c4e2ad2d2c3ccfb0b8ecf255f        refs/heads/develop      process4j       IOS
{"created": "2023-05-10T16:43:58.000000", "committer": "66115350", "message": "SOC-1264 F\u00f6renklat genom att alltid bygga allt. Uppat version"}     4726d57f1d52a64044622168509ec0eca0b5d829        refs/heads/develop      python-postgresql-patches IOS
{"created": "2023-05-08T11:26:34.000000", "committer": "66115350", "message": "Pull request #12: SOC-1321 Lagt till dom\u00e4nnamn f\u00f6r kunder\n\nMerge in IOS/spdb-tools from feature/SOC-1321-spdb-forbattra-anonymisering-av-dnsnamn to develop\n\nSquashed commit of the following:\n\ncommit fb49c95b99d9938155c0a0eea553af2908daed16\nAuthor: Secret Author <secret.author@myndigheten.se>\nDate:   Mon May 8 10:23:58 2023 +0200\n\n    SOC-1321 Lagt till dom\u00e4nnamn f\u00f6r kunder"}     d233234d0e3e5cf4c59d79852803138a7c4df4a7        refs/heads/develop      spdb-tools      IOS
{"created": "2023-05-16T13:53:53.000000", "committer": "66115683", "message": "Start av repo"}  f345cfffa2a083f99d1f489dbf42f70d15ad26b2        refs/heads/develop      spring-clients  IOS
```
## atlcli bitb create-branches
```
$ atlcli bitb create-branches --help
usage: atlcli bitb create-branches [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                          [-w WORKERS] [-l FILE] [-a SEPARATOR] [-m MESSAGE]
                          NAME

Creates a new branch for each commit id in input.

positional arguments:
  NAME                  The display name of the new branches

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -m MESSAGE, --message MESSAGE
                        Message for branch. (default: Created by create-
                        branches

Input line is commit id (first column), repo name (third column) and project
name (fourth column). Output is the new branch name followed by repo name and
the project name

```
You need REPO_WRITE permission for the repo.
### Create a branch from a branch
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | grep atlassian | atlcli bitb get-branches -n develop | atlcli bitb get-commits | atlcli bitb create-branches feature/test
refs/heads/feature/test atlassian-cli   IOS
```

## atlcli bitb delete-branches
```
$ atlcli bitb delete-branches -h
usage: atlcli bitb delete-branches [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                          [-w WORKERS] [-l FILE] [-a SEPARATOR]

Deletes a branch foreach branch name in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Input is branch name, repo and project. Output is "DELETED" followed by input
line.

```
You need REPO_WRITE permission on the repo.
### Delete a branch
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n feature/test | atlcli bitb delete-branches
DELETED refs/heads/feature/test atlassian-cli   IOS

```
## atlcli bitb create-tags
```
$ atlcli bitb create-tags --help
usage: atlcli bitb create-tags [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                      [-w WORKERS] [-l FILE] [-a SEPARATOR] [-m MESSAGE]
                      NAME

Creates a tag for each commit in input.

positional arguments:
  NAME                  The display name of the new tag

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -m MESSAGE, --message MESSAGE
                        Message for tag. (default: Created by atlcli bitb create-tags)

Input line is commit id (column 0), repo name (column 2) and project name
(column 3). Output the new tag id followed by input line.

```
### Create a tag for a specific repo on a named feature branch
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | grep atlassian | atlcli bitb get-branches -n develop \
| atlcli bitb get-commits | atlcli bitb create-tags "tag/testing"
refs/tags/tag/testing   atlassian-cli   IOS
```
## atlcli bitb get-branches-or-tags
```
$ atlcli bitb get-branches-or-tags --help
usage: atlcli bitb get-branches-or-tags [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                               [-w WORKERS] [-l FILE] [-a SEPARATOR]
                               [-n NAMES [NAMES ...]] [-d] [-i]

For each repo in input, lists or searches branch and tag names.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -n NAMES [NAMES ...], --names NAMES [NAMES ...]
                        Space separated list of regular expressions defining
                        branch or tag names. The display name us used here as
                        it is shorter. If no name is given all branches and
                        tags are returned, each on a separate line. (default:
                        None)
  -d, --displayid       Output displayid instead of id, useful for bash
                        integration (default: False)
  -i, --invert          Invert logic. Only repos with all listed names missing
                        are included in output. Only makes sense with -n
                        switch (default: False)

Input is repo (first column) and project (second column). Other columns are
ignored. Branch fully qualified names are used in the output, unless switch -d
is used. If switch -n is defined only those repos with all matching names are
included in output. Each output line consists of all matching branches and
tags, in separate columns, followed by input line. If there are multiple names
matching a pattern, the largest name is used. Name comparison is semantic
version aware. The names are split using full stop, and each part is compared.
A longer string is "larger" than a short string in a versionized name. If
there are no full stops in the name, traditional string comparison is used. If
switch -n is not defined, all branches and tags are included in output, each
on a separate line. Pipe output to atlcli bitb get-commits or atlcli bitb delete-branches or
atlcli bitb filter-branches or atlcli bitb filter-merged or atlcli bitb get-file-names or atlcli bitb create-pr or
atlcli bitb get-pr.

```
### List latest release tag (and master branch) for repos having a master branch for a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches-or-tags -n '\d+\.\d+\.\d+' master
refs/tags/0.2.1 refs/heads/master       python-postgresql-patches       IOS
```
## atlcli bitb filter-branches
```
$ atlcli bitb filter-branches --help
usage: atlcli bitb filter-branches [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                          [-w WORKERS] [-l FILE] [-a SEPARATOR]

For each branch in input, filters existing branches.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Input is a number of branch names followed by repo (next last column) and
project (last column). Only input lines where all branches exist are included
in output. Pipe output to get-commits or delete-branches or filter-
merged or get-file-names or create-pr or get-pr.
```
## atlcli bitb filter-merged
```
$ atlcli bitb filter-merged --help
usage: atlcli bitb filter-merged [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                        [-w WORKERS] [-l FILE] [-a SEPARATOR] [-i]

Foreach two branch names in input, filters merged branch pairs.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -i, --invert          Invert results, report unmerged repos. (default:
                        False)

Each input line starts with the two branch names, followed by project and repo
names. The first branch name is the outgoing branch, and the second is the
incoming branch.The last commit of the outgoing branch is compared to all
commits in the incoming branch. If this commit is found, a merge has been
performed, and the branches are included in output. Also if the incoming
branch is a parent of the outgoing branch, and there are no changes, this is
considered a merge, since they are equal. Output is same as input. Pipe output
to atlcli bitb get-commits or atlcli bitb delete-branches or atlcli bitb get-file-names or atlcli bitb create-pr
or atlcli bitb get-pr.
```
### List all repos where develop is not merged to master
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop master | \
atlcli bitb filter-merged -i
refs/heads/develop      refs/heads/master       atlassian-cli   IOS
refs/heads/develop      refs/heads/master       chassi  IOS
refs/heads/develop      refs/heads/master       hundbidrag-backend      IOS
refs/heads/develop      refs/heads/master       process4j       IOS
```
### List all repos in a project where the latest release is merged to master
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches-or-tags -n '\d+\.\d+\.\d+' master \
| atlcli bitb filter-merged
refs/tags/0.2.1 refs/heads/master       python-postgresql-patches       IOS
```

## atlcli bitb get-file-names
```
$ atlcli bitb get-file-names --help
usage: atlcli bitb get-file-names [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                         [-w WORKERS] [-l FILE] [-a SEPARATOR] [-m MAX] [-c]
                         [-n NAME]

Lists or searches file names for each branch in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -m MAX, --max MAX     Output maximum max of lines only. Use this option to
                        filter repos with a given file by giving 1 as
                        parameter. (default: None)
  -c, --count           Output number of matching files instead of names
                        (default: False)
  -n NAME, --name NAME  A regular expression defining the file names to search
                        for. The whole path is used in the search, that is if
                        the regular expression matches eanything in the path
                        to the file it is included. (default: .)

Each input line starts with a branch or tag name, followed by repo name and
then the project name. Output is input line prepended with each found file.
Pipe output to atlcli bitb get-file-urls.

```
### Searches for file name in develop branch in a project
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | \
atlcli bitb get-file-names -n pyproject.toml
bitbucket-tests/files/atrefsheadsdevelopprojectsIOSreposatlassianclirawpyproject.toml   refs/heads/develop      atlassian-cli   IOS
pyproject.toml  refs/heads/develop      atlassian-cli   IOS
pyproject.toml  refs/heads/develop      python-postgresql-patches       IOS
pyproject.toml  refs/heads/develop      spdb-tools      IOS
```
## atlcli bitb get-file-details
```
$ atlcli bitb get-file-details --help
usage: atlcli bitb get-file-details [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                           [-w WORKERS] [-l FILE] [-a SEPARATOR]
                           [-s SUBSTITUTE]

Lists file details for each file name in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -s SUBSTITUTE, --substitute SUBSTITUTE
                        Replacement pattern for separator. Default is 3 spaces
                        (default: )

Each input line starts with the file name, followed by branch name and lastly
the project name. Output is each input line prepended with last modified date,
committer, message and commit id in separate columns.
```
### Example
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | atlcli bitb get-file-names -n pyproject.toml | atlcli bitb get-file-details
2023-05-17T17:14:33.000000      secret.author@myndigheten.se  Testar  76a82c41d029e49ad0d00ca7ea920a85f7c966e3        bitbucket-tests/files/atrefsheadsdevelopprojectsIOSreposatlassianclirawpyproject.toml   refs/heads/develop      atlassian-cli      IOS
2023-04-24T17:02:43.000000      secret.author@myndigheten.se  ITUAID-17 Gjort om koden till en pythonmodul    5ed9b48e0e86ab8fd8e69f7bcc21185bea6049fa        pyproject.toml  refs/heads/develop      atlassian-cli   IOS
2023-05-10T16:43:58.000000      secret.author@myndigheten.se  SOC-1264 Förenklat genom att alltid bygga allt. Uppat version   4726d57f1d52a64044622168509ec0eca0b5d829        pyproject.toml  refs/heads/develop      python-postgresql-patches IOS
2023-05-08T11:26:34.000000      secret.author@myndigheten.se  Pull request #12: SOC-1321 Lagt till domännamn för kunder       d233234d0e3e5cf4c59d79852803138a7c4df4a7        pyproject.toml  refs/heads/develop      spdb-tools      IOS


```
## atlcli bitb get-file-urls
```
$ atlcli bitb get-file-urls --help
usage: atlcli bitb get-file-urls [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                        [-w WORKERS] [-l FILE] [-a SEPARATOR]

Lists download url for each file name in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Each input line starts with the file name, followed by branch or tag name,
repo name and lastly the project name. Output is download url followed by
input line. Pipe output to get-file-content.

```
### Searches for file name expression in develop branch in a project and gets the download urls
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | \
atlcli bitb get-file-names -n pyproject.toml | atlcli bitb get-file-urls
https://secret.git.repo/projects/IOS/repos/atlassian-cli/raw/bitbucket-tests/files/atrefsheadsdevelopprojectsIOSreposatlassianclirawpyproject.toml?at=refs/heads/develop     bitbucket-tests/files/atrefsheadsdevelopprojectsIOSreposatlassianclirawpyproject.toml      refs/heads/develop      atlassian-cli   IOS
https://secret.git.repo/projects/IOS/repos/atlassian-cli/raw/pyproject.toml?at=refs/heads/develop    pyproject.toml  refs/heads/develop      atlassian-cli   IOS
https://secret.git.repo/projects/IOS/repos/python-postgresql-patches/raw/pyproject.toml?at=refs/heads/develop        pyproject.toml  refs/heads/develop      python-postgresql-patches       IOS
https://secret.git.repo/projects/IOS/repos/spdb-tools/raw/pyproject.toml?at=refs/heads/develop       pyproject.toml  refs/heads/develop      spdb-tools      IOS
```
## atlcli bitb get-file-content
```
$ atlcli bitb get-file-content --help
usage: atlcli bitb get-file-content [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                           [-w WORKERS] [-l FILE] [-a SEPARATOR]
                           [-s SUBSTITUTE] [-e ENCODING] [-d DIRECTORY]
                           [-n NEWLINE] [-v]
                           {lines,count} ...

Downloads files and searches file contents. Matching rows, or count, are
output.

positional arguments:
  {lines,count}         'lines' will output the matching lines. 'count' will
                        output number of matching lines.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -s SUBSTITUTE, --substitute SUBSTITUTE
                        Replacement pattern for separator. Default is 3
                        spaces. (default: )
  -e ENCODING, --encoding ENCODING
                        Fallback file encoding. (default: iso-8859-1)
  -d DIRECTORY, --directory DIRECTORY
                        Trace directory. (default: .)
  -n NEWLINE, --newline NEWLINE
                        Line ending char, default is \r. (default: )
  -v, --invert-match    Select non-matching lines. (default: False)

Each inputline should have the download url in first column. Each file is
downloaded and lines are matched. Default encoding is UTF-8. If decoding
fails, the fallback encoding is used. If env.trace is specified, each
downloaded file is saved in a separate file, using the url as file name.
```
```
$ atlcli bitb get-file-content count -h
usage: atlcli bitb get-file-content count [-h] PATTERN

Outputs number of matching lines.

positional arguments:
  PATTERN     A regular expression matching the full line.

optional arguments:
  -h, --help  show this help message and exit

One column is added to the input line, the number of matching lines.
```
```

$ atlcli bitb get-file-content lines -h
usage: atlcli bitb get-file-content lines [-h] [-B BEFORE_CONTEXT] [-A AFTER_CONTEXT]
                                 PATTERN

Outputs all matching lines.

positional arguments:
  PATTERN               A regular expression matching the full line.

optional arguments:
  -h, --help            show this help message and exit
  -B BEFORE_CONTEXT, --before-context BEFORE_CONTEXT
                        Print BEFORE_CONTEXT lines of leading context.
  -A AFTER_CONTEXT, --after-context AFTER_CONTEXT
                        Print AFTER_CONTEXT lines of trailing context.

Two columns are added to the input line, line number and line contents.

```
### Searches for version row in pyproject.toml in all repos of a project 
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | atlcli bitb get-branches -n develop | \
atlcli bitb get-file-names -n '^pyproject.toml' | atlcli bitb get-file-urls | \
atlcli bitb get-file-content lines 'version.*' | atlcli tool select-columns 1 5
version = "1.0.0"       atlassian-cli
version = {attr = "postgresqlpatches.__version__"}      python-postgresql-patches
version = "0.3.0"       spdb-tools

```
### Counts the python code lines in a repo 
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | grep atlassian | atlcli bitb get-branches -n develop | \
atlcli bitb get-file-names -n '\.py' | atlcli bitb get-file-urls | \
atlcli bitb get-file-content -v count "\s*|from.*|import.*" | atlcli tool select-columns 0 2 | tail
8       toolscripts/count-group-by.py
11      toolscripts/get-version.py
8       toolscripts/join-columns.py
8       toolscripts/minus-columns.py
8       toolscripts/order-by.py
8       toolscripts/select-columns.py
8       toolscripts/sum-group-by.py
8       toolscripts/union.py
8       toolscripts/where-columns.py
8       toolscripts/where-matches.py

```

## atlcli bitb create-pr
```
$ atlcli bitb create-pr --help
usage: atlcli bitb create-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                    [-w WORKERS] [-l FILE] [-a SEPARATOR] [-r REVIEWER]
                    TITLE DESCRIPTION

Creates a pull request for each two branch names in input.

positional arguments:
  TITLE                 Pull reqeust title
  DESCRIPTION           The pull request description

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -r REVIEWER, --reviewer REVIEWER
                        A pull request reviewer (default: None)

Each line starts with the two branch names, followed by the repo name and then
project name. The first branch name is the branch to merge from, and the
second is the branch to merge to. Output is the pull request id followed by
the input line.

```
### Create pull requests for a named branch in a specific repo
```
$ atlcli bitb get-projects -n IOS | atlcli bitb get-repos | grep atlassian | \
atlcli bitb get-branches -n feature/anonymisera develop | \
atlcli bitb create-pr Anonmizing "Just for the sake of the example"
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS

```
## atlcli bitb get-pr
```
$ atlcli bitb get-pr --help
usage: atlcli bitb get-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g] [-w WORKERS]
                 [-l FILE] [-a SEPARATOR] [-s {OPEN,DECLINED,MERGED,ALL}]
                 [-d {OUT,IN,EITHER}]

Prints pull request id for each input line.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -s {OPEN,DECLINED,MERGED,ALL}, --state {OPEN,DECLINED,MERGED,ALL}
                        Pull request state. (default: OPEN)
  -d {OUT,IN,EITHER}, --direction {OUT,IN,EITHER}
                        Branch direction if only one branch in input. IN means
                        branch name is incoming. OUT means branch name is
                        outgoing. EITHER means branch name is matched to both
                        incoming and outgoing branches. (default: EITHER)

Input starts with two optional branch names, followed by repo and project
name. If two branch names are given, the first branch name is the outgoing
branch and the second is the incoming branch. If only project and repo names
are defined in input, all pull requests are listed. If one branch is defined
in input, output depends on --direction switch. Output is pull request id
followed by outgoing branch, incoming branch, repo and project. Pipe output to
get-pr-files or get-pr-details or filter-pr or put-pr or merge-
pr or delete-pr .

```
### Lists all open pull requests for a range of projects
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-pr
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
2       refs/heads/bugfix/PRV-14-justera-depoly-skript  refs/heads/develop      xye-processmotor-src    IOS
13      refs/heads/feature/mountable-secrets    refs/heads/dev  xy-helm-deployment-library      IOS_OS_CHASSI
12      refs/heads/feature/upload-staging-prod  refs/heads/dev  xy-helm-deployment-library      IOS_OS_CHASSI
4       refs/heads/feature/CI2-435-fixa-chassi  refs/heads/master       xy-quarkus-template     IOS_OS_CHASSI
```
### Lists all open pull requests to develop for a range of projects
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-branches -n develop | \
atlcli bitb get-pr -d IN
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
2       refs/heads/bugfix/PRV-14-justera-depoly-skript  refs/heads/develop      xye-processmotor-src    IOS
```
### Lists all open pull requests involving develop
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-branches -n develop | atlcli bitb get-pr
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
2       refs/heads/bugfix/PRV-14-justera-depoly-skript  refs/heads/develop      xye-processmotor-src    IOS

```
### Lists all open pull requests from a branch to a branch
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | \
atlcli bitb get-branches -n feature/anonymisera develop | atlcli bitb get-pr
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
```
### Lists declined pull requests for a project
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-pr -s DECLINED
97      refs/heads/feature/anonymisera  refs/heads/dummy/merge2 atlassian-cli   IOS
83      refs/heads/feature/ITUAID-17-gor-atlassian-cli-till-en-pythonmodul      refs/heads/develop      atlassian-cli   IOS
101     refs/heads/BETA-214-cucumber-installation       refs/heads/develop      hundbidrag-backend      IOS
80      refs/heads/test/BETA-163-quarkus-live   refs/heads/develop      hundbidrag-backend      IOS
10      refs/heads/develop      refs/heads/master       spdb-tools      IOS
7       refs/heads/bugfix/SOC-1330-spdb-spdb-tools-formodar-cp1252-kodning-av-text      refs/heads/develop      spdb-tools      IOS
6       refs/heads/develop      refs/heads/bugfix/SOC-1330-spdb-spdb-tools-formodar-cp1252-kodning-av-text      spdb-tools      IOS

```
## atlcli bitb get-pr-files
```
$ atlcli bitb get-pr-files --help
usage: atlcli bitb get-pr-files [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                       [-w WORKERS] [-l FILE] [-a SEPARATOR]

Prints affected file names of a pull request for each pull request in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name. Only OPEN pull
request are included in output. Output is each affected file on a separate
line followed by the input line.The file name is the name in the to-branch,
but if the file is deleted, it is the name from the from-branch. Since the
underlying api is not paged, data could be truncated, this is indicated by the
first line in output having TRUNCATED instead of a file name

```
### Show pull request files for a pull requests
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | \
atlcli bitb get-branches -n feature/anonymisera develop | atlcli bitb get-pr | atlcli bitb get-pr-files | tail
test/expected/get-file-names-count.output       128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-file-names-filter.output      128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-file-names-max.output 128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-file-names.output     128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-file-urls.output      128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-pr-all.output 128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-pr-declined.output    128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-pr-details-json.output        128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-pr-details.output     128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
test/expected/get-pr-diff.output        128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
```
## atlcli bitb get-pr-details
```
$ atlcli bitb get-pr-details --help
usage: atlcli bitb get-pr-details [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                         [-w WORKERS] [-l FILE] [-a SEPARATOR] [-j]

Prints pull request details for each pull request in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -j, --json            Outputs json string instead of columns. (default:
                        False)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name. Output is title,
created time, state, version, author, reviewer, status, canMerge, link to pull
request in bitbucket, followed by input line.

```
### Get details of all pull requests in a project
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | \
atlcli bitb get-branches -n feature/anonymisera develop | atlcli bitb get-pr | atlcli bitb get-pr-details
Anonmizing      2023-06-13T12:51:03.407000      OPEN    0       secret.author@myndigheten.se  None    N/A     True    https://secret.git.repo/projects/IOS/repos/atlassian-cli/pull-requests/128    128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS

```
## atlcli bitb filter-pr
```
$ atlcli bitb filter-pr --help
usage: atlcli bitb filter-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                    [-w WORKERS] [-l FILE] [-a SEPARATOR] [-i]
                    [-s {APPROVED,UNAPPROVED,NEEDS_WORK}]

For each pull request in input, filter only those pull requests which can be
merged and contains changes.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -i, --invert          Invert results, report pull request which cannot be
                        merged or have no changes. (default: False)
  -s {APPROVED,UNAPPROVED,NEEDS_WORK}, --status {APPROVED,UNAPPROVED,NEEDS_WORK}
                        Filter on status. Match if at least one reviewer och
                        participant has set this status. If this switch is set
                        no other tests are made, invert switch is honored
                        though. (default: None)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name. Only OPEN pull
request are included in output. Pipe output to get-pr-files or get-pr-
details or filter-pr or put-pr or merge-pr or delete-pr .

```
### Finds all mergeable pull requests in a set of projects
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-pr | atlcli bitb filter-pr
128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS
2       refs/heads/bugfix/PRV-14-justera-depoly-skript  refs/heads/develop      xye-processmotor-src    IOS
12      refs/heads/feature/upload-staging-prod  refs/heads/dev  xy-helm-deployment-library      IOS_OS_CHASSI
4       refs/heads/feature/CI2-435-fixa-chassi  refs/heads/master       xy-quarkus-template     IOS_OS_CHASSI
```
### Finds all pull requests in a project which cannot be merged 
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | atlcli bitb get-pr | atlcli bitb filter-pr -i
13      refs/heads/feature/mountable-secrets    refs/heads/dev  xy-helm-deployment-library      IOS_OS_CHASSI
```
## atlcli bitb get-pr-diff
```
$ atlcli bitb get-pr-diff --help
usage: atlcli bitb get-pr-diff [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                      [-w WORKERS] [-l FILE] [-a SEPARATOR] [-s SUBSTITUTE]
                      [-e ENCODING] [-n NEWLINE] [-d DIRECTORY]

Prints pull request diffs for each pull request in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)
  -s SUBSTITUTE, --substitute SUBSTITUTE
                        Replacement pattern for separator. Default is 3 spaces
                        (default: )
  -e ENCODING, --encoding ENCODING
                        Fallback file encoding. (default: iso-8859-1)
  -n NEWLINE, --newline NEWLINE
                        Line ending char, default is \r. (default: )
  -d DIRECTORY, --directory DIRECTORY
                        Trace directory. (default: .)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name.Output is each
line in diff followed by the input line.
```

## atlcli bitb put-pr
```
$ atlcli bitb put-pr --help
usage: atlcli bitb put-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g] [-r USER]
                 [-w WORKERS] [-l FILE] [-a SEPARATOR]
                 {APPROVED,UNAPPROVED,NEEDS_WORK}

Changes pull request state for each pull request in input.

positional arguments:
  {APPROVED,UNAPPROVED,NEEDS_WORK}
                        Pull request status.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -r USER, --user USER  Bitbucket user name. If not set, value is read from
                        environment variable BITBUCKET_USER (default: None)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

The state for the user is passed as a parameter. State is changed only for
open pull requests. Each input starts with the pull request id, followed by
two branch names (ignored) and then the repo nameand lastly the project name.
Output is state followed by input line.
```
Unfortunately it is impossible to figure out your user name, so you will have to supply it on command line or
define it as an environment variable.

## atlcli bitb merge-pr
```
$ atlcli bitb merge-pr --help
usage: atlcli bitb merge-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                   [-w WORKERS] [-l FILE] [-a SEPARATOR]
                   MESSAGE

Merge each pull request in input if possible

positional arguments:
  MESSAGE               Merge commit message.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name. Output is input
and the new state prepended. If the pull request cannot be merged this is
reported as CANNOT-MERGE.
```

## atlcli bitb delete-pr
```
$ atlcli bitb delete-pr --help
$ atlcli bitb delete-pr --help
usage: atlcli bitb delete-pr [-h] [-k TOKEN] [-u URL] [-o TIMEOUT] [-t] [-g]
                    [-w WORKERS] [-l FILE] [-a SEPARATOR]

Deletes each pull request in input.

optional arguments:
  -h, --help            show this help message and exit
  -k TOKEN, --token TOKEN
                        Your personal bitbucket token, see https://confluence.
                        atlassian.com/bitbucketserver/personal-access-
                        tokens-939515499.html. If not set, token is read from
                        environment variable BITBUCKET_TOKEN. (default: None)
  -u URL, --url URL     Bitbucket server url. If not set, value is read from
                        environment variable BITBUCKET_URL (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        Timeout in requests to server. The environment
                        variable BITBUCKET_TIMEOUT overrides (default: 10)
  -t, --trace           Turns on tracing of request/response to bitbucket
                        server (default: False)
  -g, --debug           Turns on debug printouts (default: False)
  -w WORKERS, --workers WORKERS
                        Number of worker threads. Default is 5. Be aware that
                        you could be kicked for DOS attack if set too large.
                        (default: 5)
  -l FILE, --file FILE  If given, input is read from this file. Otherwise
                        input is read from stdin. (default: None)
  -a SEPARATOR, --separator SEPARATOR
                        Separator. Accepts escaped character. The environment
                        variable BITBUCKET_SEPARATOR overrides. (default: \t)

Each input starts with the pull request id, followed by two branch names
(ignored) and then the repo nameand lastly the project name. Output is input
line with "DELETED" prepended.
```
### Delete a pull request 
```
$ atlcli bitb get-projects -n 'IOS.*' | atlcli bitb get-repos | \
atlcli bitb get-branches -n feature/anonymisera develop | atlcli bitb get-pr | atlcli bitb delete-pr
DELETED 128     refs/heads/feature/anonymisera  refs/heads/develop      atlassian-cli   IOS

```
## Testing
There is a subdirectory for testing with a separate readme.


