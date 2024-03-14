import datetime
from urllib.parse import urlparse
from pathlib import Path
from os import path


def to_file_name(directory, url):
    """
    Creates a file name from a request url. This is used when tracing file download for testing purposes.
    :param directory: The directory to store the file
    :param url: The request url
    :return: a file name to be used to store the downloaded file
    """
    parts = urlparse(url)
    base = f"{parts.query}_{parts.params}_{parts.fragment}_{parts.path}"\
        .replace("/", "").replace("=", "").replace("__", "").replace("_", "").replace("-", "")
    filename = path.normpath(Path(directory) / base)
    return filename


def to_time(timestamp):
    """
    Creates a date and time from an atlassian timestamp
    :param timestamp: The timestamp to convert.
    :return: A time object which can be sorted.
    """
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%dT%H:%M:%S.%f')