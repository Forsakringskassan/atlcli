import logging
import os
import subprocess
import re


def get_version(file, base_version) -> str:
    """
    Generic code allowing for generation of versions based on commit ids.

    Include this file in the modules __init__.py file, and call it like this:
    ``__version__ = get_version(<base_version>, __file__)``

    If executing from a git source tree the version is calculated using base_version, current commit and branch name.
    If in master branch, base_version is used. In all other branches the base version is extended with a plus followed
    by the timestamp of the commit (down to second) followed by the first 15 charactes of the branch name. The version
    is written to the file VERSION in the catalog identified by file parameter. If executed outside a git repo,
    the VERSION file is read and returned.

    In order for this to work you need to add MANIFEST.in at the root level. MANIFEST.in should add the VERSION
    file, like this: ``include <module>/VERSION``, <module> is the name of your module. And ``dynamic = ["version"]`` in
    ``[project]`` section in the pyprocjet.toml file. A new section ``[tool.setuptools.dynamic]`` in pyproject.toml
    should contain ``version = {attr = "<module>.__version__"}``, where <module> is the name of your module
    :param file: Should be the __file__
    :param base_version: In form major.minor.fix
    :return: The calculated version for this commit.
    """
    version = base_version
    current_catalog = os.getcwd()
    logging.debug(f'current_catalog={current_catalog}')
    installation_catalog = os.path.dirname(os.path.realpath(file))
    logging.debug(f'installation_catalog={installation_catalog}')
    version_file_name = os.path.join(installation_catalog, 'VERSION')
    # Get current branch
    os.chdir(installation_catalog)
    logging.debug(f'os.getcwd()=={os.getcwd()}')
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        branch = result.stdout.strip().replace("'", "")

        # Get commit
        result = subprocess.run(["git", "rev-parse", "--verify", "HEAD"],
                                shell=True, capture_output=True, text=True)
        commit = result.stdout.strip().replace("'", "")
        # Get timestamp
        result = subprocess.run(["git", "show", "-s", "--date=format:'%Y%m%d%H%M%S'", "--format=%cd", commit],
                                shell=True, capture_output=True, text=True)
        timestamp = result.stdout.strip().replace("\'", "").replace("'", "")
        if branch != "master":
            if branch == "release":
                pre_name = "rc"
            elif branch == "develop":
                pre_name = "b"
            else:
                pre_name = "a"
            version = f'{base_version}{pre_name}{timestamp}'
        with open(version_file_name, 'w') as version_file:
            version_file.write(version)
    else:
        with open(version_file_name, 'r') as version_file:
            version = version_file.read()
    os.chdir(current_catalog)
    logging.debug(f'os.getcwd()=={os.getcwd()}')
    return version





