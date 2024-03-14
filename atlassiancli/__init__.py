import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from shared import moduleversion

BASE_VERSION = '1.2.0'

__version__ = moduleversion.get_version(__file__, BASE_VERSION)

__all__ = [
    "__version__"
]


def get_version() -> str:
    version = moduleversion.get_version(__file__, BASE_VERSION)
    return version
