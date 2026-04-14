"""
The purpose of this module is to hold reusable code. It icontains only functions.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def decode(line, coding):
    """
    Decodes a line according to the coding
    :param line: The line to decode
    :param coding: The encoding to use
    :return: a successfully decoded line and None, or None and the caught UnicodeDecodeError
    """
    try:
        return line.decode(coding).rstrip(), None
    except UnicodeDecodeError as e:
        return None, e


