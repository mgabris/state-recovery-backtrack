import random
import sys
import argparse


class RC4:
    def __init__(self, state=None, key=None, perm_size=8):
        if state is None:
            self.N = perm_size
            if key is None:
                key = [random.randint(0, self.N - 1) for _ in range(self.N)]
            self.key_setup(key)
        else:
            self.initialize_state(state)

    def initialize_state(self, state=None):
        if state is None:
            self.i, self.j = 0, 0
            self.S = [i for i in range(self.N)]
        else:
            self.i, self.j = state[0]
            self.S = state[1][:]
        self.N = len(self.S)

    @property
    def state(self):
        return [[self.i, self.j], self.S]
    

    def key_setup(self, K):
        self.initialize_state()
        j = 0
        for i in range(self.N):
            j = (j + self.S[i] + K[i % len(K)]) % self.N
            self.swap(i, j)

    def prg(self):
        self.i = (self.i + 1) % self.N
        self.j = (self.j + self.S[self.i]) % self.N
        self.swap(self.i, self.j)
        return self.S[(self.S[self.i] + self.S[self.j]) % self.N]

    def swap(self, x, y):
        self.S[x], self.S[y] = self.S[y], self.S[x]

    def keystream(self, amount):
        return [self.prg() for _ in range(amount)]

    def inverse_prg(self):
        self.swap(self.i, self.j)
        self.j = (self.j - self.S[self.i]) % self.N
        self.i = (self.i - 1) % self.N

    def inverse_state(self, steps):
        for _ in range(steps):
            self.inverse_prg()