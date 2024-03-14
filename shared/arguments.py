"""
The purpose of this module is to hold reusable code. It contains only functions.
"""
from sys import stderr
import os
import platform
from .environment import Environment

from argparse import ArgumentParser
# Environment variables
SERVER_USER = "{}_USER"
SERVER_TIMEOUT = "{}_TIMEOUT"
SERVER_PORT = "{}_PORT"
SERVER_URL = "{}_URL"
SERVER_TOKEN = "{}_TOKEN"
SERVER_SEPARATOR = "{}_SEPARATOR"


def add_common(parser, server, script_name, workers=True, user=False):
    """Adds common command line parameters to parser.
    Parameters
    ----------
    parser : ArgumentParser
        The argument parser for the calling script.
    server :
        'BITBUCKET' or 'JIRA'
    script_name :
        The name of the script to be used in debugging
    workers : bool
        If the script has worker threads, if so the switch -w is added.
    user : bool
        If true adds -r switch to the parser. This is used for a few scrips where you need to identify a user when
        calling the bitbucket server. Unfortunately you cannot figure out the current user name.
    ----------
    """
    server_token = SERVER_TOKEN.format(server)
    parser.add_argument('-k', '--token',
                        help='Your personal bitbucket token, see '
                             'https://confluence.atlassian.com/bitbucketserver/personal-access-tokens-939515499.html. '
                             'If not set, token is read from environment variable {}.'.format(server_token))
    server_url = SERVER_URL.format(server)
    parser.add_argument('-u', '--url',
                        help=f'Bitbucket server url. If not set, value is read from environment variable {server_url}')
    parser.add_argument('-p', '--port', type=int, help=f'Bitbucket server port. Main purpose is for testing.')
    server_timout = SERVER_TIMEOUT.format(server)
    parser.add_argument('-o', '--timeout', type=int, default=10,
                        help='Timeout in requests to server. The environment variable {} overrides'.format(server_timout))
    parser.add_argument('-t', '--trace', action='store_true',
                        help='Turns on tracing of request/response to bitbucket server')
    parser.add_argument('-g', '--debug', action='store_true',
                        help='Turns on debug printouts')
    parser.add_argument('-z', '--script', default=script_name, help='Script name in debug output')
    if user:
        server_user = SERVER_USER.format(server)
        help_text = 'Bitbucket user name. If not set, value is read from environment variable {}'.format(server_user)
        parser.add_argument('-r', '--user', help=help_text)
    if workers:
        # Only called with false for get-projects. In this case we don't want input file as well,
        # or have any use for a separator
        workers_help = 'Number of worker threads. Default is 5. Be aware that you could be kicked for ' \
                       'DOS attack if set too large.'
        parser.add_argument('-w', '--workers',
                            default=5,
                            type=int,
                            help=workers_help)
        parser.add_argument('-l', '--file',
                            help='If given, input is read from this file. Otherwise input is read from stdin.')
    add_separator(parser, server)


def add_separator(parser, server):
    server_separator = SERVER_SEPARATOR.format(server)
    separator_help = f"Separator. Accepts escaped character. The environment variable {server_separator} overrides."
    parser.add_argument('-a', '--separator', default='\\t', help=separator_help)


def get_common_arguments(parser, args, server):
    """Retrieves common parameters from args using the parser.
    Parameters
    ----------
    parser : ArgumentParser
        The argument parser for the calling script.
    args :
        The args retrieved from the parser with this call:
        'args = parser.parse_args()'
    server :
        'BITBUCKET' or 'JIRA'
    script : str
        The name of the calling script.
    Returns
    -------
    Environment
        An object with properties token, url, timeout, trace, debug, version
    """
    script = args.script
    server_token = SERVER_TOKEN.format(server)
    if args.token is None and os.getenv(server_token, None) is None:
        stderr.write("\033[31m{}: No token defined\033[0m{}".format(script, os.linesep))
        stderr.write("{}{}".format(parser.format_help(), os.linesep))
        exit(2)
    token = args.token if args.token is not None else os.environ[server_token]
    server_url = SERVER_URL.format(server)
    if args.url is None and os.getenv(server_url, None) is None:
        stderr.write("\033[31m{}: No url defined\033[0m{}".format(script, os.linesep))
        stderr.write("{}{}".format(parser.format_help(), os.linesep))
        exit(2)
    url = (args.url if args.url is not None else os.getenv(server_url)).strip("http://")
    server_timout = SERVER_TIMEOUT.format(server)
    timeout_env = os.getenv(server_timout, None)
    timeout = timeout_env if timeout_env is not None else args.timeout
    trace = args.trace
    debug = args.debug
    separator = get_separator(args, server)
    version = 'Python-' + platform.python_version()
    port = args.port
    result = Environment(token, url, timeout, separator, trace, debug, version, script, port)
    return result


def get_separator(args, server):
    if hasattr(args, 'separator'):
        server_separator = SERVER_SEPARATOR.format(server)
        separator_env = os.getenv(server_separator, None)
        separator = separator_env if separator_env is not None else bytes(args.separator, "utf-8").decode("unicode_escape")
    else:
        separator = None
    return separator


def get_user(parser, args, server, script):
    """Gets the user from command line or environment.
    Parameters
    ----------
    parser : ArgumentParser
        The argument parser for the calling script.
    args :
        The args retrieved from the parser with this call:
        'args = parser.parse_args()'
    server :
        'BITBUCKET' or 'JIRA'
    script : str
        The name of the calling script.
    Returns
    -------
    str
        The user as defined on command line or the environment
    ----------

    """
    server_user = SERVER_USER.format(server)
    if args.user is None and os.getenv(server_user, None) is None:
        stderr.write("\033[31m{}: No user defined\033[0m{}".format(script, os.linesep))
        stderr.write("".format(parser.format_help(), os.linesep))
        exit(2)
    user = args.user if args.user is not None else os.environ[server_user]
    return user
