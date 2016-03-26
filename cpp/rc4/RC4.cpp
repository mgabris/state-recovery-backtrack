#include "assert.h"

#include "RC4.hpp"


RC4::RC4(State * state) : state(state) {};

int RC4::prg() {
    state->i = (state->i + 1) % state->N;
    state->j = (state->j + state->S[state->i]) % state->N;
    std::swap(state->S[state->i], state->S[state->j]);
    return state->S[(state->S[state->i] + state->S[state->j]) % state->N];
}

void RC4::keystream(int r, std::vector<int> &keystream) {
    keystream.clear();
    for (int i = 0; i < r; ++i) {
        keystream.push_back(prg());
    }
}

void RC4::inverse_prg() {
    std::swap(state->S[state->i], state->S[state->j]);
    state->j = (state->j - state->S[state->i] + state->N) % state->N;
    state->i = (state->i - 1 + state->N) % state->N;
}

void RC4::inverse_state(int steps) {
    for (int i = 0; i < steps; ++i) {
        inverse_prg();
    }
}