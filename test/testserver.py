#!python -X utf8
import os
import sys
from sys import exit, stderr, path
from http.server import HTTPServer, BaseHTTPRequestHandler
from argparse import ArgumentDefaultsHelpFormatter,  ArgumentParser
from uuid import UUID

STOPPING = "stopping\n".encode('utf-8')

path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from shared import arguments as arg, conversion

directory = None
get_files = {}
get_trace = {}
post_trace = {}
put_trace = {}
delete_trace = {}
verb_trace = {}
verb_trace["GET"] = get_trace
verb_trace["POST"] = post_trace
verb_trace["PUT"] = put_trace
verb_trace["DELETE"] = delete_trace


def validate_uuid4(uuid_string):

    """
    https://gist.github.com/ShawnMilo/7777304
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.
    result = str(val) == uuid_string
    return result


class TraceData:
    def __init__(self, uuid):
        self.uuid = uuid
        self.script_name = None
        self.type = None
        self.verb = None
        self.addr = None
        self.request_body = None
        self.response_body = None
        self.response_status = None


class TestServer(BaseHTTPRequestHandler):
    def _set_headers(self, response_code):
        self.send_response(response_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if len(get_files) != 0:
            key = conversion.to_file_name(directory, self.path)
            if key not in get_files:
                self.do_any(get_trace)
            else:
                file = get_files[key]
                self._set_headers(200)
                for l in file:
                    self.wfile.write(l)
        else:
            self.do_any(get_trace)

    def do_POST(self):
        self.do_any(post_trace)

    def do_PUT(self):
        self.do_any(put_trace)

    def do_DELETE(self):
        self.do_any(delete_trace)

    def do_any(self, dict):
        headers = self.headers
        contentLengthHeader = headers.get('Content-Length')
        content_len = 0 if contentLengthHeader is None else int(contentLengthHeader)
        body = self.rfile.read(content_len).decode('utf-8') if content_len != 0 else None
        path = self.path
        if path == "/stop":
            self.send_response(200)
            self.send_header("Content-type", "application/text")
            self.send_header("Content-Length", str(len(STOPPING)))
            self.end_headers()
            self.wfile.write(STOPPING)
            exit()
        if path not in dict:
            stderr.write(f"Could not find {path} in dict{os.linesep}")
            stderr.flush()
            self._set_headers(404)
            # self.send_response(404)
        else:
            if body is None:
                trace = dict[path]
                self._set_headers(trace.response_status)
                self.wfile.write(trace.response_body.encode("utf-8"))
            else:
                body_dict = dict[path]
                if type(body_dict) is TraceData:
                    stderr.write(f"Missing body in trace file {os.linesep}")
                    exit(1)
                if body not in body_dict:
                    stderr.write(f"{body} not in body_dict {os.linesep}")
                    exit(1)
                trace = body_dict[body]
                self._set_headers(trace.response_status)
                if trace.response_body != None:
                    self.wfile.write(trace.response_body.encode("utf-8"))


def init_trace(tracefile):
    if os.path.isdir(tracefile):
        global directory
        directory = tracefile
        for file_name in os.listdir(tracefile):
            key = conversion.to_file_name(tracefile, file_name)
            get_files[key] = []
            with open(key, "rb") as file:
                for line in file:
                    get_files[key].append(line)
        return
    uuid_trace = {}
    with open(tracefile, 'r') as file:
        for line in file:
            line = line.rstrip()
            if len(line) == 0:
                continue
            columns = line.split(separator)
            uuid = columns[0]
            if not validate_uuid4(uuid):
                continue
            if len(columns) < 4:
                stderr.write("columns < 4: {}{}".format(line, os.linesep))
                exit(1)
            script_name = columns[1]
            type = columns[2]
            verb = columns[3]
            addr = columns[4]
            status = int(columns[5])
            message = columns[6] if len(columns) > 6 else None
            if uuid not in uuid_trace:
                uuid_trace[uuid] = TraceData(uuid)
            trace = uuid_trace[uuid]
            if type == "request":
                trace.script_name = script_name
                trace.addr = addr
                trace.verb = verb
                trace.request_body = message
            elif type == "response":
                if trace.script_name is None:
                    stderr.write("trace.script_name = None. uuid={} type={}{}".format(uuid, type, os.linesep))
                    exit(1)
                if trace.script_name != script_name:
                    stderr.write("trace.script_name={}. script_name={}{}".format(trace.script_name, script_name, os.linesep))
                    exit(1)
                if trace.addr != addr:
                    stderr.write("trace.addr={}. addr={}{}".format(trace.addr, addr, os.linesep))
                    exit(1)
                if trace.verb != verb:
                    stderr.write("trace.verb={}. verb={}{}".format(trace.verb, verb, os.linesep))
                    exit(1)
                trace.response_body = message
                trace.response_status = status
    for uuid in uuid_trace.keys():
        trace = uuid_trace[uuid]
        dictionary = verb_trace[trace.verb]
        if trace.request_body is None:
            # GET usually dont have a body
            dictionary[trace.addr] = trace
        else:
            # POST usually has a body, we need request body information to diffentiate between POSTS
            if trace.addr not in dictionary:
                dictionary[trace.addr] = {}
            body_dict = dictionary[trace.addr]
            body_dict[trace.request_body] = trace
    for uuid in uuid_trace.keys():
        trace = uuid_trace[uuid]
        type = trace.type
        if trace.response_status is None:
            stderr.write("trace.response_status = None. uuid={} type={}{}".format(uuid, type, os.linesep))
            exit(1)


if __name__ == '__main__':
    global separator
    descr = 'A test server to be used to emulate at bitbucket server given a recorded trace file'
    parser = ArgumentParser(description=descr, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('tracefile', metavar='TRACEFILE', help='The name of the trace file')
    arg.add_common(parser, 'BITBUCKET', os.path.basename(sys.argv[0]))
    args = parser.parse_args()
    separator = arg.get_separator(args, 'BITBUCKET')

    server_address = ('', 8000)
    init_trace(args.tracefile)
    httpd = HTTPServer(server_address, TestServer)
    httpd.serve_forever()
