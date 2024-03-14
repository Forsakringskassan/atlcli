# Python postgres patches
## Table of Contents
[**Purpose**](#purpose)\
[**Installation**](#installation)\
[**Background**](#background)\
[**Requirements**](#requirements)\
[**Design**](#design)\
[**Automation**](#automation)\
[**Development**](#development)\
[**To do**](#todo)
## Purpose <a name="purpose"/>
This module installs postgresql sql files in a sequenced manner. The sequence is determined by the file names, 
se below under [Design](#design).
## Installation <a name="installation"></a>
```
python3 -m pip install postgresqlpatches
```
### Set environment variable passwords
You can call the postgresqlpatches module using your prefix of choice. When not defining a prefix, 
the default prefix POSTGRESQL is used.
If you use the default password in postgresql you do not need to set the POSTGRESQL_POSTGRES_PASSWORD.
When done it should look something like:
```
$ printenv | grep PASSWORD
<prefix>_POSTGRES_PASSWORD=********
<prefix>_PATCHES_PASSWORD=********
<prefix>_HUNDBIDRAG_PASSWORD=********
```
### Try the example
```
cd examples
$ pwd
/very/secret/path/git/python-postgresql-patches/examples
$ python3 -m postgresqlpatches -l debug './hundbidrag/*.sql'
```
## Background <a name="background"></a>
We had a need for an open source tool to organize our postgresql patches. The google search resulted in tools
that where written in script languages unsupported by our organisation. Or impossible to install because of 
red tape.

We decided to write a simple tool in python. Python is fully supported by our organisation.
## Requirements <a name="requirements"></a>
### Seamless integration with our existing database
The transition to the new tool is done by a pgsql dump.
### Simple execution order
Scripts should be executed in a sequence determined by their file names.

We have no need for dependency analysis.
### Multiple databases
The system should support multiple databases.
### Schema change should be performed by a superuser
We use the account "postgres" for schema changes.
### Installation state
Installation state should be held in a separate database.
### Allow modular database schemas
It should be possible to organize scripts into separate catalogs.
## Design <a name="design"></a>
### Encoded file name
Each patch file is made of 5 parts, separated by dot, and ended with the sql extension.
1. Database name
2. Major version, 8 digits. Use YYYYMMDD. Major of 00000000 has special meaning, see below.
3. Minor version, 4 digits. Use sequence or mmss. Minor of 0000 has special meaning with major of 00000000.
4. Username
5. Description

For example, the baseline for the patches database is 
```
    patches.00000000.0000.postgres.baseline.sql
    |       |        |    |        |
    1 = database     |    |        |
            2 = major|    |        |
                     3 = minor     |
                          4 = user |
                                   5 = description
```
### Database passwords
Database passwords are retrieved from environment variables. The variable should be named ```{prefix}{USER}_PASSWORD```
The default environment variable for the superuser is POSTGRESQL_POSTGRES_PASSWORD, and the 
default password for the application should be stored in a variable named POSTGRESQL_PATCHES_PASSWORD.

The baseline script contains this code to create the user using the environment variable:

```
\set pwd `bash -c "echo $PATCHES_POSTGRESQL_TEMPORARY_USER_PASSWORD"`
create user patches
    createdb
    encrypted password :'pwd';
```
If there is no matching environment variable, the username is used for password, default password for user postgres 
is postgres.
### Bootstrapping 
Scripts with a major of 00000000 are run only if the database does not exist. If the database doesn't exist, all 
scripts with a major of 00000000 are run.

The script with major of 00000000 and minor 0000 is run using psql since the pg_dump is used for creation of this file.

All other scripts are run using psycopg2

When all scripts with a major of 00000000 have been executed, we know that the patches database exists. We connect 
to the patches database and updates it with the scripts already executed. 

### Globbing parameters
Input to the patches module is a list of glob names. All files matching the glob names are candidates for execution.

### Execution logic
All found script files are sorted in database, major, minor order. The path to the file is not considered here. You 
can refactor the script catalogs as long as you keep the first three parts of the file name.

Before running a script, the patches database is checked if the script has been run already. Each script is only run 
once.

After the script is executed the patches database is updated.
## Build system
### Versions
We wanted to include the timestamp of the latest commit in all builds except for builds from master thread. 

The version is defined in pyproject.toml as an attribute. When building proper the code resides in a git repo and the 
timestamp is retrieved from git. But during the build process the code is moved outside the gitrepo. So the first call 
to the __version__ attribute is stored in the file VERSION to be used in later stages.

The version is also used to tag the commit after build. So each tag has to be unique. We believe 1 second to be enough 
granular.
## Automation <a name="automation"></a>
Automation has its own chapter because technicians need to install the build system. Techies don't need to read the 
next chapter...

Automation code resides in catalog autobuild. 

Account creation is documented for the case when you need to set up a development system. For a build machine the 
accounts should not be personal.
### Design principles
#### Virtual environment
The build server is run in its own virtual environment in order to isolate it from any changes to the site.
#### Same git repo and development environment
The automation code resides with the code it builds, in the same git repo. The same development process is used for 
automation code as for the base code. The developers development machine is used for testing the automation code.
#### One buildbot server per repo
Since the build server code is tied to the code it builds, only one git repo can be built using a build server. The 
consequence is that each automatically built repo will have its own port on the build server.
#### Buildbot server is configured using environment variables
The most important variable is PYTHON_POSTGRESQL_PATCHES_BRANCHES which defines which branches to build. It is 
documented below. 
#### Git flow
We follow a simple git flow workflow. Nexus repo to upload to is decided by the branch name.

Merges to master branch will upload the wheel file to 
```
https://python.repo.mynd.se/repository/production/
```
Merges to release branch will upload the wheel file to
```
https://python.repo.mynd.se/repository/releases/
```
Merges to develop branch will upload the wheel file to
```
https://python.repo.mynd.se/repository/develop/
```
Commits to all other branches till be uploaded to 
```
https://python.repo.mynd.se/repository/snapshots/
```
### Installation
#### Install postgresql on build machine
```
rpm install or whaterver
```
#### Configure pip 
to look at python.repo.mynd.se

#### Clone
Clone the whole repo on the build server:
```
$ cd <git path>
$ git clone ssh://git@bitb.mynd.se:7999/ios/python-postgresql-patches.git
```
#### Configure environment
##### Database access 
Set database environment variables as described in [Installation](#installation), use the default POSTGRESQL prefix.

##### Nexus and twine
Set up our account in nexus. Log in to python.repo.mynd.se using the web gui

Set environment variables for twine. Check your environment when done.
```
$ printenv | grep TWINE
TWINE_PASSWORD=**********
TWINE_USERNAME=*********
```
##### Nexus IQ
Set up our account in nexus iq. Log in to secscan.mynd.se using the web gui and SSO. Create a token.

Set environment variables. Check your environment when done.
```
$ printenv | grep TWINE
NEXUS_IQ_PASSWORD=**********
NEXUS_IQ_USERNAME=*********
```
#### Configure buildbot server
Cd to autobuild catalog:
```
$ cd python-postgresql-patches/autobuild
```
Run setup script:
```
$ ./setup.sh
```
Follow the printed instructions at the end of the script.
### Build steps
#### worker_preparation
This step is default from buildbot and cannot be configured.
#### git-checkout
When the repo monitor decides that there is something to build, it activates an agent and this is the first build step.
The branch is already decided. The code doing the checkout is rather complex but easy to configure. The catalog
is rather deep down below automation/master_root/my_master.
#### python-build
```
python -m build -n 
```
is run in the checked out catalog.
#### install-wheel
```
sh install.sh <wheel> 
```
is run in the verify catalog.
#### postgresql-drop-databases
This step drops all databases and users. The purpose is to prepare for module execution in later step.
#### run-postgresqlpatches
```
sh run.sh 
```
is run in the verify catalog. The patches and hundbidrag databases will be created.
#### scan-nexus-iq
Jake will be run in catalog verify by executing:
```
sh verify.sh 
```
The result of the scan will be presented at the bottom of the build detail view.
#### twine-upload
```
python -m twine upload <nexusrepo> <wheel>  
```
is executed.
#### bitbucket-tag
```
atlcli bitb create-tags <version>  
```
will be exeucted with proper input to tag the current commit with the same version as uploaded to nexus.
## Development <a name="development"></a>
Follow the instructions in [Automation](#automation), except the part setting environment variable 
PYTHON_POSTGRESQL_PATCHES_BRANCHES
### Build
```
$ python3 -m build -n
```
### Install .whl file
```
$ python3 -m pip install dist/postgresqlpatches-x.y.z-py3-none-any.whl
```
### Upload to nexus
```
$ python3 -m twine upload --repository-url https://python.repo.mynd.se/repository/production/ dist/postgresqlpatches-<version>-py3-none-any.whl
```
### Analyzing using jake in catalog verify
The catalog verify contains three scripts, install.sh, run.sh and verify.sh. Run these scripts from the verify 
directory. You will get a nexus iq report.

These scripts are run from automation. The purpose is to isolate the postgresqlpatches module and run jake on this 
module only. Running jake in the build environment causes a lot of false positive reports from the build environment.  
### Making changes to automation
The environment.sh script mentioned above will set PYTHON_POSTGRESQL_PATCHES_BRANCHES to current branch. 

In order to test your changes, stop and restart buildbot. Commit and push. Wait for the build. When you are happy 
with the changes, talk to the techie to update automation code on build server by a git pull. And restart the 
buildbot server.
### Resetting the automation environment
Start a new shell if you are in the sandbox.

Delete some files:
```
$ cd <git path>/python-postgresql-patches/automation
$ pushd master_root
$ rm -rf sandbox
$ cd my_master
$ rm -rf buildbot.tac state.sqlite workers gitpoller-workdir
```
Rerun the installation script
```
$ popd
$ ./setup.sh
```
## To do <a name="todo"></a>
### Automatic tests
The code needs automatic tests. Both positive and negative. These should be executed in the automation pipeline.  
### Better error handling
Narrow down the caught exceptions to what is actually thrown. Update documentation.

