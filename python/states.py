class SpritzState:
    def __init__(self, state=None, registers=None, permutation=None, string=None):
        if state:
            registers = state[0]
            permutation = state[1]
        elif string:
            # TODO: not very safe
            state = eval(string)
            registers = state[0]
            permutation = state[1]
        elif registers is None or permutation is None:
            raise TypeError(
                'expected either registers and permutation or string'
            )
        # format of registers is list, [i, j, k, z, a, w], same as in cipher
        # implementation class
        self.i, self.j, self.k, self.z = registers[:4]
        self.w = registers[-1]
        self.S = permutation[:]
        self.free = set(range(len(permutation))) - set(permutation)

    def swap(self):
        self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]

    # conversion from variables (stored in class) to list (used in cipher 
    # class) and vice versa
    @property
    def registers(self):
        return [self.i, self.j, self.k, self.z, 0, self.w]

    @registers.setter
    def registers(self, value):
        self.i, self.j, self.k, self.z = value[:4]
        self.w = value[-1]

    @property
    def state(self):
        return [[self.i, self.j, self.k, self.z, 0, self.w], self.S]

    @property
    def size(self):
        return len(self.S)
    
    def __deepcopy__(self, memo):
        return SpritzState([self.registers, self.S])

    def __eq__(self, other):
        return self.registers == other.registers and self.S == other.S

    def __str__(self):
        return '[{}, {}]'.format(
            str(self.registers),
            str(self.S)
        )


class RC4State:
    def __init__(self, state=None, registers=None, permutation=None, string=None):
        if state:
            registers = state[0]
            permutation = state[1]
        elif string:
            # TODO: not very safe
            state = eval(string)
            registers = state[0]
            permutation = state[1]
        elif registers is None or permutation is None:
            raise TypeError(
                'expected either registers and permutation or string'
            )
        # format of registers is list, [i, j, k, z, a, w], same as in cipher
        # implementation class
        self.i, self.j = registers
        self.S = permutation[:]
        self.free = set(range(len(permutation))) - set(permutation)

    def swap(self):
        self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]

    # conversion from variables (stored in class) to list (used in cipher 
    # class) and vice versa
    @property
    def registers(self):
        return [self.i, self.j]

    @registers.setter
    def registers(self, value):
        self.i, self.j = value

    @property
    def state(self):
        return [[self.i, self.j], self.S]

    @property
    def size(self):
        return len(self.S)
    
    def __deepcopy__(self, memo):
        return RC4State([self.registers, self.S])

    def __eq__(self, other):
        return self.registers == other.registers and self.S == other.S

    def __str__(self):
        return '[{}, {}]'.format(
            str(self.registers),
            str(self.S)
        )
