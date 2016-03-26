#include "assert.h"

#include "Spritz.hpp"


Spritz::Spritz(State * state) : state(state) {};

void Spritz::shuffle() {
    ASSERT(false, "Shuffle not implemented");
}

void Spritz::squeeze(int r, std::vector<int> &keystream) {
    if (state->a > 0) {
        shuffle();
    }
    keystream.clear();
    for (int i = 0; i < r; ++i) {
        keystream.push_back(drip());
    }
}

int Spritz::drip() {
    if (state->a > 0) {
        shuffle();
    }
    update();
    return output();
}

void Spritz::update() {
    state->i = (state->i + state->w) % state->N;
    state->j = (state->k + state->S[ (state->j + state->S[state->i]) % state->N ]) % state->N;
    state->k = (state->i + state->k + state->S[state->j]) % state->N;
    std::swap(state->S[state->i], state->S[state->j]);
}

int Spritz::output() {
    state->z = state->S[(state->j + state->S[
        (state->i + state->S[(state->z + state->k) % state->N]) % state->N]) % state->N
    ];
    return state->z;
}

void Spritz::keystream(int r, std::vector<int> &keystream) {
    squeeze(r, keystream);
}

void Spritz::inverse_output() {
    int N = state->N;
    bool found = false;
    for (int p = 0; p < N; ++p) {
        int zk = (p + state->k) % N;
        int iSzk = (state->i + state->S[zk]) % N;
        int jSiSzk = (state->j + state->S[iSzk]) % N;
        if (state->z == state->S[jSiSzk]) {
            state->z = p;
            found = true;
            break;
        }
    }
    ASSERT(found, "not found previous z");
}

void Spritz::inverse_update() {
    std::swap(state->S[state->i], state->S[state->j]);
    int N = state->N;
    state->k = (state->k - state->i - state->S[state->j] + 2 * N) % N;
    bool found = false;
    for (int p = 0; p < N; ++p) {
        int jSi = (p + state->S[state->i]) % N;
        int j_val = (state->k + state->S[jSi]) % N;
        if (state->j == j_val) {
            state->j = p;
            found = true;
            break;
        }
    }
    ASSERT(found, "not found previous j");
    state->i = (state->i - state->w + N) % N;
}

void Spritz::inverse_drip() {
    inverse_output();
    inverse_update();
}

void Spritz::inverse_state(int steps) {
    for (int i = 0; i < steps; ++i) {
        inverse_drip();
    }
}