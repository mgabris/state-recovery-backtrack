import math
import random


class Spritz:

    def gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a

    def __init__(self, state=None, key=None, state_size=8):
        if state is None:
            self.N = state_size
            self.D = math.ceil(math.sqrt(self.N))
            if key is None:
                key = [random.randint(0, self.N - 1) for _ in range(self.N)]
            self.key_setup(key)
        else:
            self.initialize_state(state)

    def initialize_state(self, state=None):
        if state is None:
            self.i, self.j, self.k, self.z, self.a = 0, 0, 0, 0, 0
            self.w = 1
            self.S = [i for i in range(self.N)]
        else:
            self.N = len(state[1])
            self.D = math.ceil(math.sqrt(self.N))
            self.i, self.j, self.k, self.z, self.a, self.w = state[0]
            self.S = state[1][:]

    @property
    def state(self):
        return [[self.i, self.j, self.k, self.z, self.a, self.w], self.S]

    def key_setup(self, K):
        self.initialize_state()
        self.absorb(K)

    def absorb(self, I):
        for v in I:
            self.absorb_byte(v)

    def absorb_byte(self, b):
        # first low(b), then high(b)
        self.absorb_nibble(b % self.D)
        self.absorb_nibble(b // self.D)

    def absorb_nibble(self, x):
        if self.a == self.N//2:
            self.shuffle()
        self.swap(self.a, self.N//2 + x)
        self.a += 1

    def absorb_stop(self):
        if self.a == self.N//2:
            self.shuffle()
        self.a += 1

    def shuffle(self):
        self.whip(2 * self.N)
        self.crush()
        self.whip(2 * self.N)
        self.crush()
        self.whip(2 * self.N)
        self.a = 0

    def whip(self, r):
        for v in range(r):
            self.update()
        while True:
            self.w = (self.w + 1) % self.N
            if Spritz.gcd(self.w, self.N) == 1:
                break

    def crush(self):
        for v in range(self.N//2):
            if self.S[v] > self.S[self.N-1-v]:
                self.swap(v, self.N-1-v)

    def squeeze(self, r):
        if self.a > 0:
            self.shuffle()
        p = [self.drip() for _ in range(r)]
        return p

    def keystream(self, amount):
        return self.squeeze(amount)

    def drip(self):
        if self.a > 0:
            self.shuffle()
        self.update()
        return self.output()

    def update(self):
        self.i = (self.i + self.w) % self.N
        self.j = (self.k + self.S[(self.j + self.S[self.i]) % self.N]) % self.N
        self.k = (self.k + self.i + self.S[self.j]) % self.N
        self.swap(self.i, self.j)

    def output(self):
        self.z = self.S[(self.j + self.S[
            (self.i + self.S[(self.z + self.k) % self.N]) % self.N]) % self.N
        ]
        return self.z

    def swap(self, x, y):
        self.S[x], self.S[y] = self.S[y], self.S[x]

    def inverse_update(self):
        self.swap(self.i, self.j)
        self.k = (self.k - self.i - self.S[self.j]) % self.N
        val = (self.j - self.k) % self.N
        for p in range(self.N):
            if self.j == (self.k + self.S[(p + self.S[self.i]) % self.N]) % self.N:
                self.j = p
                break
        self.i = (self.i - self.w) % self.N

    def inverse_output(self):
        for p in range(self.N):
            if self.z == self.S[(self.j + self.S[(self.i + self.S[(p + self.k) % self.N]) % self.N]) % self.N]:
                self.z = p
                break

    def inverse_drip(self):
        # restore old value of z
        self.inverse_output()
        # restore old value of other registers
        self.inverse_update()

    def inverse_state(self, steps):
        for _ in range(steps):
            self.inverse_drip()
