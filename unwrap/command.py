#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point for command-line interface.
"""
from __future__ import absolute_import, print_function, unicode_literals, division

import argparse
import locale
import os
import sys

from . import __version__, __description__
from .core import Joiner

def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description=__description__)
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="unwrap {ver}".format(ver=__version__),
        help="Show version number and exit.")
    parser.add_argument(
        "in_file",
        metavar="INPUT",
        help="Input file.")
    parser.add_argument(
        "out_file",
        metavar="OUTPUT",
        help="Output file.")
    parser.add_argument(
        "-f", "--format",
        default="txt",
        help="Output format.")
    parser.add_argument(
        "-e", "--encoding",
        default=locale.getpreferredencoding(),
        help="Character encoding.")
    parser.add_argument(
        "-s", "--stats",
        action="store_true",
        help="Print statistics on exit.")
    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=2,
        help="Number of iterations.")
    return parser.parse_args(args)


def run():
    args = parse_args(sys.argv[1:])

    with open(args.in_file, "rb") as in_file:
        lines = in_file.read().decode(args.encoding).split(os.linesep)

    joiner = Joiner(lines)
    joiner.iterate(args.iterations - 1)
    paragraphs = list(joiner)

    with open(args.out_file, "wb") as out_file:
        for paragraph in paragraphs:
            out_file.write((paragraph.text + os.linesep).encode(args.encoding))
            if paragraph.uncertain:
                out_file.write(("### UNCERTAIN ###" + os.linesep).encode(args.encoding))

    if args.stats:
        stats = joiner.stats
        print("Input lines:                  {}".format(len(lines)))
        print("Ouput lines:                  {}".format(len(paragraphs)))
        print("First line average length:    {}".format(stats["first avg"]))
        print("First line length deviation:  {}".format(stats["first dev"]))
        print("Middle line average length:   {}".format(stats["middle avg"]))
        print("Middle line length deviation: {}".format(stats["middle dev"]))


if __name__ == "__main__":
    run()
