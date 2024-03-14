import os
from sys import stderr, stdout


def print_error(env, addr, response, script_name):
    """
    Prints an error message in red to stderr.
    :param env: The environment object. Needed for the requested url
    :param addr: The requested resource
    :param response: The response object
    :param script_name: The name of the originalting script
    :return: Nothing
    """
    stderr.write("\033[31m{}: Could not connect to {}{}. {}:{}\033[0m{}".
                 format(script_name, env.url, addr, response.status, response.read().decode('utf-8'), os.linesep))


def print_debug(env, message):
    """
    Prints a debug message to stderr if env.debug is set.
    :param env: The environment object. Tests if the member debug is set.
    :param message: The message to print.
    :return: Nothing
    """
    if env.debug:
        stderr.write(f"debug ({env.script}): {message}\n")


def write(args):
    """
    Prints the parameters to output ignoring exceptions occurring from broken pipe. This happens when you pipe
    the output to head for example
    :param args: An object to be printed. If a list, each item is printed on a separate line.
    """
    try:
        if type(args) is list:
            for line in args:
                print(line)
        else:
            print(args)
        stdout.flush()  # jalla jalla
    except Exception: ## broken pipe
        return