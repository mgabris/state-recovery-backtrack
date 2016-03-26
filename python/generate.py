#!/usr/bin/python3

import random

from rc4.cipher import RC4
from spritz.cipher import Spritz
from states import RC4State, SpritzState
from cli import parse_generate_args


State = None
Cipher = None


def generate_rc4_random_state(size):
    # registers i, j
    # registers = [random.randint(0, size-1) for _ in range(2)]
    registers = [0, 0]
    permutation = [i for i in range(size)]
    random.shuffle(permutation)
    return RC4State([registers, permutation])


def generate_spritz_random_state(size):
    # registers i, j, k
    registers = [random.randint(0, size-1) for _ in range(3)]
    # state is just before update+output and after last shuffle, so a = 0
    # z = 0 as we didn't produce any output yet
    # registers z, a
    registers += [0, 0, 1]
    w = random.randint(1, size-1)
    while Spritz.gcd(w, size) != 1:
        w = random.randint(1, size-1)
    registers[-1] = w
    permutation = [i for i in range(size)]
    random.shuffle(permutation)
    return SpritzState([registers, permutation])


def generate_spritz_random_special_state(size):
    assert size & 0x1 == 0
    # i - even
    # j, k - even
    # registers = [0] + [2 * random.randint(0, size//2-1) for _ in range(2)]
    registers = [2 * random.randint(0, size//2-1) for _ in range(3)]
    # z = 0, a = 0
    registers += [0, 0]
    w = random.randint(1, size-1)
    while Spritz.gcd(w, size) != 1:
        w = random.randint(1, size-1)
    registers += [w]

    even_vals = [2*i for i in range(size//2)]
    random.shuffle(even_vals)
    odd_vals = [2*i + 1 for i in range(size//2)]
    random.shuffle(odd_vals)

    permutation = []
    # odd indices have even values
    # even indices have odd values
    for i in range(size//2):
        permutation.append(odd_vals[i])
        permutation.append(even_vals[i])

    return SpritzState([registers, permutation])


def generate_revealed_state(from_state, revealed):
    size = from_state.size
    indexes_to_reveal = random.sample([i for i in range(size)], revealed)
    permutation = []
    for i in range(size):
        value = None
        if i in indexes_to_reveal:
            value = from_state.S[i]
        permutation.append(value)
    return State([from_state.registers, permutation])


def good_wrong_values(state, wrong_indexes, wrong_values):
    assert len(wrong_indexes) == len(wrong_values)
    for i, v in zip(wrong_indexes, wrong_values):
        if state.S[i] == v:
            return False
    return True


def wrong_revealed_state(revealed_state, number_of_wrong):
    revealed_indexes = []
    revealed_values = set()
    for i, v in enumerate(revealed_state.S):
        if v is not None:
            revealed_indexes.append(i)
            revealed_values.add(v)
    wrong_indexes = random.sample(revealed_indexes, number_of_wrong)
    wrong_indexes_values = set()
    for i in wrong_indexes:
        wrong_indexes_values.add(revealed_state.S[i])
    wrong_values_set = set(range(revealed_state.size)) - revealed_values | wrong_indexes_values
    wrong_values = random.sample(wrong_values_set, number_of_wrong)
    while not good_wrong_values(revealed_state, wrong_indexes, wrong_values):
        wrong_values = random.sample(wrong_values_set, number_of_wrong)
    j = 0
    permutation = revealed_state.S[:]
    for i in wrong_indexes:
        assert permutation[i] is not None
        permutation[i] = wrong_values[j]
        j += 1
    return State([revealed_state.registers, permutation])


def more_revealed_state(backtrack_state, revealed_state, to_reveal):
    not_revealed_indexes = set()
    for i, v in enumerate(revealed_state.S):
        if v is None:
            not_revealed_indexes.add(i)

    indexes_to_reveal = random.sample(not_revealed_indexes, to_reveal)
    permutation = revealed_state.S[:]
    for i in indexes_to_reveal:
        permutation[i] = backtrack_state.S[i]

    assert sum([(0 if x is None else 1) for x in revealed_state.S]) + to_reveal == sum([(0 if x is None else 1) for x in permutation])
    return State([revealed_state.registers, permutation])


def random_revealed_state(from_state, to_reveal):
    size = from_state.size
    indexes_to_reveal = random.sample([i for i in range(size)], to_reveal)
    values_to_reveal = random.sample([i for i in range(size)], to_reveal)
    permutation = [None for _ in range(size)]
    for i in range(to_reveal):
        permutation[indexes_to_reveal[i]] = values_to_reveal[i]
    return State([from_state.registers, permutation])


def generate_states(size, shift, amount, generate):
    states = []
    for _ in range(amount):
        starting_state = generate(size)
        cipher = Cipher(starting_state.state)
        cipher.keystream(shift)
        backtrack_state = State([cipher.state[0], [None for _ in range(size)]])
        states.append([
            starting_state,
            backtrack_state,
            shift
        ])
    return states
        

def read_states(input_file):
    states = []
    while True:
        initial = input_file.readline()
        if initial == '':
            break
        revealed = input_file.readline()
        shift = int(input_file.readline())
        states.append([
            State(string=initial), 
            State(string=revealed),
            shift
        ])
    return states


def write_states(states_list):
    for generated in states_list:
        for el in generated:
            print(el)


def reveal_values_simple(amount, base_state):
    size = base_state.size
    indexes_to_reveal = random.sample([i for i in range(size)], amount)
    permutation = [None for _ in range(size)]
    for i in indexes_to_reveal:
        permutation[i] = base_state.S[i]
    return State([base_state.registers, permutation])


def reveal_values_special(even, odd, base_state):
    size = base_state.size
    assert size%2 == 0
    even_indexes = random.sample([2*i for i in range(size//2)], even)
    odd_indexes = random.sample([2*i+1 for i in range(size//2)], odd)
    permutation = [None for _ in range(size)]
    for i in even_indexes:
        permutation[i] = base_state.S[i]
    for i in odd_indexes:
        permutation[i] = base_state.S[i]
    return State([base_state.registers, permutation])


def reveal_random_values_simple(amount, base_state):
    size = base_state.size
    indexes_to_reveal = random.sample([i for i in range(size)], amount)
    values_to_reveal = random.sample([i for i in range(size)], amount)
    permutation = [None for _ in range(size)]
    for i in range(amount):
        permutation[indexes_to_reveal[i]] = values_to_reveal[i]
    return State([base_state.registers, permutation])


def reveal_random_values_special(even, odd, base_state):
    size = base_state.size
    even_indexes = random.sample([2*i for i in range(size//2)], even)
    even_index_values = random.sample([2*i+1 for i in range(size//2)], even)
    odd_indexes = random.sample([2*i+1 for i in range(size//2)], odd)
    odd_index_values = random.sample([2*i for i in range(size//2)], even)

    permutation = [None for _ in range(size)]
    for i in range(even):
        assert even_indexes[i] % 2 == 0
        permutation[even_indexes[i]] = even_index_values[i]
    for i in range(odd):
        assert odd_indexes[i] % 2 == 1
        permutation[odd_indexes[i]] = odd_index_values[i]

    return State([base_state.registers, permutation])


def move_state(base_state, steps):
    cipher = Cipher(base_state.state)
    cipher.keystream(steps)
    return State(cipher.state)


def main(args):
    global State, Cipher
    
    if args.rc4:
        State = RC4State
        Cipher = RC4
    elif args.spritz:
        State = SpritzState
        Cipher = Spritz

    states = []
    if args.input:
        states = read_states(args.input)
    else:
        if args.rc4:
            f = generate_rc4_random_state
        elif args.spritz:
            f = generate_spritz_random_state
            if args.special:
                f = generate_spritz_random_special_state
        states = generate_states(
            args.size,
            args.prefix_length,
            args.amount,
            f
        )
    assert len(states) != 0

    for i in range(len(states)):
        moved_state = move_state(states[i][0], args.prefix_length)
        revealed_state = states[i][1]
        if args.simple:
            if args.reveal_random:
                revealed_state = reveal_random_values_simple(args.preselected, moved_state)
            elif args.reveal_new_random:
                raise NotImplementedError()
            elif args.reveal:
                revealed_state = reveal_values_simple(args.preselected, moved_state)
            elif args.reveal_new:
                raise NotImplementedError()
            elif args.reveal_wrong:
                raise NotImplementedError()
            elif args.reveal_new_wrong:
                raise NotImplementedError()
        else:
            # args.special
            if args.reveal_random:
                revealed_state = reveal_random_values_special(args.preselected_even, args.preselected_odd, moved_state)
            elif args.reveal_new_random:
                raise NotImplementedError()
            elif args.reveal:
                revealed_state = reveal_values_special(args.preselected_even, args.preselected_odd, moved_state)
            elif args.reveal_new:
                raise NotImplementedError()
            elif args.reveal_wrong:
                raise NotImplementedError()
            elif args.reveal_new_wrong:
                raise NotImplementedError()
        
        states[i][1] = revealed_state


    write_states(states)


if __name__ == '__main__':
    main(parse_generate_args())