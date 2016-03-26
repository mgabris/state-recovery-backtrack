#!/usr/bin/python3

import argparse
import random

from cipher import Spritz


def parse_args():
    parser = argparse.ArgumentParser(
        description="Naive implementation of Spritz stream cipher"
    )
    parser.add_argument(
        "perm_size", metavar="N",
        type=int,
        help="size of permutation"
    )
    parser.add_argument(
        "keystream_amount", metavar="amount",
        type=int,
        help="amount of desired keystream"
    )

    parser.add_argument(
        "-v", "--verbosity",
        type=int, default=0,
        help="level of verbosity"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-k", "--key",
        action="store_true",
        help=(
            "read key from stdin as python array, "
            "if omitted random key of size N is set"
        )
    )
    group.add_argument(
        "-s", "--state",
        action="store_true",
        help=(
            "read initial state from stdin as python arrays, "
            "no key setup"
        )
    )

    args = parser.parse_args()
    return args


def main(args):
    in_key, in_state = [], []
    if args.key:
        in_key = [int(i) for i in input()[1:-1].split(",")]
    elif args.state:
        """
        inp = input().split("],")
        assert len(inp) == 2
        print(inp)
        in_state = [
            [int(i) for i in inp[0][2:].split(",")],
            [int(i) for i in inp[1][2:-2].split(",")]
        ]
        """
        in_state = eval(input())
    else:
        in_key = [random.randint(0, args.perm_size - 1)
                  for _ in range(args.perm_size)]
    cipher = Spritz(in_state, in_key, args.perm_size)

    if args.verbosity >= 1:
        print("key:")
        print(in_key)
        print("state after key setup:")
        print([cipher.i, cipher.j, cipher.k, cipher.z, cipher.a, cipher.w])
        print(cipher.S)

    keystream = cipher.squeeze(args.keystream_amount)

    if args.verbosity >= 2:
        print("state after squeezing:")
        print([cipher.i, cipher.j, cipher.k, cipher.z, cipher.a, cipher.w])
        print(cipher.S)

    if args.verbosity >= 1:
        print("keystream:")
    print(keystream)
    # print(" ".join(str(i) for i in keystream))


if __name__ == '__main__':
    args = parse_args()
    main(args)
