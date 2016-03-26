#!/usr/bin/python3

import sys
import pickle

import cli


def main(args):
    stats = pickle.load(args.file)
    if args.command:
        print(args.file.name, end=' ')
        print(stats.argv)
    stats.print_stats(args.verbosity)


if __name__ == '__main__':
    main(cli.parse_stats_printer_args())

