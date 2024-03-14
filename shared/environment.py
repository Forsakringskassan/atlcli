"""
This module contains the class Environment, used to represent variables given as command line options or
environment variables.
"""


class Environment:
    def __init__(self, token, url, timeout, separator, trace, debug, version, script, port=None):
        self.token = token
        self.url = url
        self.timeout = timeout
        self.sep = separator
        self.trace = trace
        self.debug = debug
        self.version = version
        self.script = script
        self.port = port

