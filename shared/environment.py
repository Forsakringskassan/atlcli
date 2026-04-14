"""
This module contains the class Environment, used to represent variables given as command line options or
environment variables.
"""


class Environment:
    def __init__(self, token, url, timeout, separator, trace, debug, loglevel, version, script, port=None):
        self.token = token
        self.url = url
        self.timeout = timeout
        self.sep = separator
        self.trace = trace
        self.debug = debug
        self.loglevel = loglevel
        self.version = version
        self.script = script
        self.port = port

    def __repr__(self):
        return (f'token={self.token}, url={self.url}, timeout={self.timeout}, separator={hex(ord(self.sep))}, '
                f'trace={self.trace}, debug={self.debug}, loglevel={self.loglevel}, version={self.version}, '
                f'script={self.script}, port={self.port}')

