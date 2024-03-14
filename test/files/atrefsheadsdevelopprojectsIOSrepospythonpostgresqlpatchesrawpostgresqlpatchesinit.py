import os
import subprocess
import re
base_version = '0.2.1'

catalog = os.path.dirname(os.path.realpath(__file__))
version_file_name = os.path.join(catalog, 'VERSION')
name_re = re.compile('[^0-9A-Za-z\.]')
# Get current branch
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

    __version__ = base_version
    if branch != "master":
        branch_tag = name_re.sub("", branch)[:20]
        __version__ = f"{base_version}+{timestamp}.{branch_tag}"
    with open(version_file_name, 'w') as version_file:
        version_file.write(__version__)
else:
    with open(version_file_name, 'r') as version_file:
        __version__ = version_file.read()

__all__ = [
    "__version__"
]



