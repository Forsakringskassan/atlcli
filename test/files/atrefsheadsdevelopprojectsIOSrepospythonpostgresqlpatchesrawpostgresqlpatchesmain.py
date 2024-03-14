#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
from postgresqlpatches import patches


def parse_args():
    """
    Adds arguments and parses the command line.
    :return: The configured argsparser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('globs', metavar='G', nargs='*', help='a glob expression to identify sql files')
    parser.add_argument('-p', '--prefix', default='POSTGRESQL_', help='Environment variables prefix')
    loglevels = ['error', 'warning', 'info', 'debug']
    parser.add_argument('-l', '--loglevel', choices=loglevels, default='info', help='Sets logging level')
    return parser.parse_args()


_nameToLevel = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


def main():
    """
    :return: 0 if success else 1
    """
    args = parse_args()
    logging.basicConfig(level=_nameToLevel[args.loglevel],
                        format='%(asctime)-15s %(levelname)-7s %(module)s %(message)s')
    logging.debug(f'Program arguments: {args}')
    globs_list = []
    for g in args.globs:
        globs_list.append(g)
    success = patches.apply_patches(globs_list, args.prefix)
    if not success:
        logging.error(f"Failed executing patches")
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())

if __name__ == '__patches__':
    exit(main())
