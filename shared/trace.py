import json
import os
import uuid
from sys import stderr


def trace_response(guid, script_name, verb, addr, status, body=None):
    """Prints a trace of a response to stderr. Should be wrapped in a test for trace variable
    Parameters
    ----------
    guid : uuid
        The uuid returned from trace_request
    script_name : str
        The calling script name
    verb : str
        The http verb to print in trace
    addr : str
        The url to be printed
    status : int
        The response status to be recorded
    body :
        The data to be printed
    """
    trace_type(guid, script_name, verb, addr, "response", status, body)


def trace_request(script_name, verb, addr, message=None):
    """Prints a trace of a request to stderr. Call should be wrapped in a test for trace variable
    Parameters
    ----------
    script_name : str
        The calling script name
    verb : str
        The http verb to print in trace
    addr : str
        The url to be printed
    message :
        The request body to be printed
    Returns
    -------
    uuid
        A unique identifier for the request/response
    """
    guid = uuid.uuid4()
    trace_type(guid, script_name, verb, addr, "request", -1, message)
    return guid


def trace_type(guid, script_name, verb, addr, type, status, message):
    jmessage = "" if message is None else message if isinstance(message, str) else json.dumps(message)
    stderr.write(f"{guid}\t{script_name}\t{type}\t{verb}\t{addr}\t{status}\t{jmessage}{os.linesep}")
