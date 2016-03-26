import argparse


def parse_benchmark_args():
    parser = argparse.ArgumentParser(
        description='Spritz KPA state extraction benchmark'
    )

    parser.add_argument(
        'input',
        type=argparse.FileType('r'),
        help='run backtrack on each state from file INPUT'
    )


    parser.add_argument(
        '-fp', '--force_prefix_length',
        type=int,
        help='cuts skipped keystream prefix to '
             'FORCE_PREFIX_LENGTH (in case it is larger), this setting is not '
             'overriden by input data'
    )
    parser.add_argument(
        '-ns', '--no_stop',
        action='store_true',
        help='don\'t stop backtrack when corect state is found, but continue '
             'search for every possibility'
    )

    # heuristics, optimalizations of backtrack
    parser.add_argument(
        '-pc', '--prefix_check',
        action='store_true',
        help='enables check for consistency with skipped prefix of keystream, '
             'check is performed at start of every backtrack call'
    )
    parser.add_argument(
        '-pcc', '--prefix_check_continue',
        action='store_true',
        help='in prefix check, don\'t stop when missing value in computation '
             'of z'
    )
    parser.add_argument(
        '-pccw', '--prefix_check_continue_write',
        action='store_true',
        help='in prefix check, write z to permutation when index is known and '
             'value at that index is None and continue'
    )
    parser.add_argument(
        '-pcg', '--prefix_check_guess',
        action='store_true',
        help='prefix check is performed after each guess'
    )
    parser.add_argument(
        '-kgo', '--keystream_guess_order',
        action='store_true',
        help='change order of guesses from range(N) to numbers in keystream '
             'first, missing values after'
    )
    parser.add_argument(
        '-lgo', '--last_guess_order',
        action='store_true',
        help='check for z_t in state before guessing last '
             'value (SiSzk)'
    )
    parser.add_argument(
        '-slg', '--skip_last_guess',
        action='store_true',
        help='only with -lgo, optimization from Knudsen\'s paper, when known_z is in S and '
             'all values other than SiSzk next step are alredy guessed, skip '
             'guessing position of known_z'
    )

    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        default=3,
        help='level of verbosity (=3)'
    )
    parser.add_argument(
        '-nsl', '--no_stats_log',
        action='store_true',
        help='disable pickling of stats class after experiment'
    )

    args = parser.parse_args()
    return args


def parse_stats_printer_args():
    parser = argparse.ArgumentParser(
        description='Loads and prints pickled stats object'
    )
    parser.add_argument(
        'file',
        type=argparse.FileType('rb'),
        help='pickled stats file to load'
    )
    parser.add_argument(
        '-c', '--command',
        action='store_true',
        help='print also filename and parameters of benchmark'
    )
    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        default=3,
        help='level of verbosity (=3)'
    )

    args = parser.parse_args()
    return args


def parse_generate_args():
    parser = argparse.ArgumentParser(
        description='Generator of Spritz cipher test files, prints everything to stdout'
    )

    parser.add_argument(
        '-i', '--input',
        type=argparse.FileType('r'),
        help='read state from file instead of generating him'
    ) 

    cipher = parser.add_mutually_exclusive_group(required=True)
    cipher.add_argument(
        '--rc4',
        action='store_true',
        help='generate RC4 states'
    )
    cipher.add_argument(
        '--spritz',
        action='store_true',
        help='generate Spritz states'
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '-rw', '--reveal_wrong',
        action='store_true',
        help='NOT IMPLEMENTED, change correct revealed values from revealed '
             'to wrong ones and write modified file to stdout'
    )
    mode.add_argument(
        '-rnw', '--reveal_new_wrong',
        action='store_true',
        help='NOT IMPLEMENTED, add new wrong revealed values '
             'to wrong ones and write modified file to stdout'
    )
    mode.add_argument(
        '-r', '--reveal',
        action='store_true',
        help='reveal values in backtrack '
             'state in random positions (discard previous revealed values) '
             'and write modified file to stdout'
    )
    mode.add_argument(
        '-rn', '--reveal_new',
        action='store_true',
        help='NOT IMPLEMENTED, reveal new values in backtrack '
             'state in random positions and write modified file to stdout'
    )
    mode.add_argument(
        '-rr', '--reveal_random',
        action='store_true',
        help='reveal random values in backtrack '
             'state in random positions (discard any previous revealed values) '
             'and write modified file to stdout'
    )

    mode.add_argument(
        '-rnr', '--reveal_new_random',
        action='store_true',
        help='NOT IMPLEMENTED, reveal new random values in backtrack '
             'state in random positions '
             'and write modified file to stdout'
    )

    type_of_state = parser.add_mutually_exclusive_group()
    type_of_state.add_argument(
        '--simple',
        action='store_true',
        help='simple state'
    )
    type_of_state.add_argument(
        '--special',
        action='store_true',
        help='special state'
    )

    # parameters of generated states
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=8,
        help='size of randomly generated permutation (=8)'
    )
    parser.add_argument(
        '-p', '--preselected',
        type=int,
        default=0,
        help='number of preselected randomly generated permutation values '
             'before backtrack (=0)'
    )
    parser.add_argument(
        '-pe', '--preselected_even',
        type=int,
        default=0,
        help='number of preselected randomly generated permutation values '
             'before backtrack (=0)'
    )
    parser.add_argument(
        '-po', '--preselected_odd',
        type=int,
        default=0,
        help='number of preselected randomly generated permutation values '
             'before backtrack (=0)'
    )
    parser.add_argument(
        '-a', '--amount',
        type=int,
        default=1000,
        help='number of states to generate (=1000)'
    )
    parser.add_argument(
        '-pl', '--prefix_length',
        type=int,
        default=0,
        help='lengthz of keystream from start after which the starting state of '
             'backtrack is (=0) '
    )
    
    args = parser.parse_args()
    return args
