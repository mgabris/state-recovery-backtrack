"""Poor mans tests for cipher implementation
Currently just tests 'by hand', no testutil (probably won't be needed)
"""

import random
from copy import deepcopy

from cipher import Spritz


def random_state(size):
    # registers = [i,j,k,z,a,w]
    registers = [random.randint(0, size-1) for _ in range(3)]
    # state just before update+output, after last shuffle so a = 0
    registers += [0, 0, 1]
    w = random.randint(1, size-1)
    while Spritz.gcd(w, size) != 1:
        w = random.randint(1, size-1)
    registers[-1] = w
    state = [i for i in range(size)]
    random.shuffle(state)
    return [registers, state]


def state_intialization():
    N = 8
    rs = random_state(N)
    print('rs', rs)
    c = Spritz(state=rs)
    print('constructor state', c.state)
    c.initialize_state(rs)
    print('cs', c.state)

def inverse_transformation():
    N = 32

    rs = random_state(N)
    print('rs', rs)
    
    c = Spritz(state=rs)
    print('cs', c.state)
    
    starting = deepcopy(c.state)

    AM = 3000
    ks = c.keystream(AM)
    # print('ak', c.state)
    
    c.inverse_state(AM)
    print('ai', c.state)
    print(c.state == starting)
    # print(ks)

def main():
    inverse_transformation()

if __name__ == '__main__':
    main()