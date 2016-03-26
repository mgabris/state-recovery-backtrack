#include <iostream>

#include <algorithm>
#include <vector>
#include <string>

#include "assert.h"
#include "common.h"

#include "backtrack.hpp"

#include "RC4.hpp"
#include "State.hpp"

using namespace std;

std::vector<int> keystream;
State * result_state = nullptr;
int result_step = 0;
bool stop = true;

Stats * stats;

bool forward_correct(State &state, int start, int amount) {
    ASSERT(keystream.size() > start+amount+1, "need more keystream");

    State tmp(state);
    RC4 cipher(&tmp);
    std::vector<int> checked_keysteam;
    cipher.keystream(amount, checked_keysteam);
    for (int i = 0; i < amount; ++i) {
        if (checked_keysteam[i] != keystream[start+i]) {
            return false;
        }
    }
    return true;
}

bool start(State &state, int step) {
    if (state.assigned == state.N) {
        // state is fully filled
        if (forward_correct(state, step, 5 * state.N)) {
            ASSERT(result_state == nullptr, "found second compliant state");
            result_state = new State(state);
            result_step = step;
            if (stop) {
                return true;
            }
        }
        return false;
    }
    return set_i(state, step);
}

bool set_i(State &state, int step) {
    int old_i = state.i;
    state.i = (state.i + 1) % state.N;

    bool result = guess_Si(state, step);
    
    state.i = old_i;
    return result;
}

bool guess_Si(State &state, int step) {
    stats->was[0][state.assigned]++;

    if (state.S[state.i] != -1) {
        stats->no_guess[0][state.assigned]++;
        return set_j(state, step);
    } 
    state.assigned += 1;
    for (int Si = 0; Si < state.N; ++Si) {
        if (state.used[Si])
            continue;
        stats->guesses += 1;
        state.S[state.i] = Si;
        state.used[Si] = true;

        bool result = set_j(state, step);

        state.used[Si] = false;
        if (result) {
            return result;
        }
    }
    state.S[state.i] = -1;
    state.assigned -= 1;
    return false;
}

bool set_j(State &state, int step) {
    int old_j = state.j;
    state.j = (state.j + state.S[state.i]) % state.N;
    std::swap(state.S[state.i], state.S[state.j]);

    bool result = guess_Si_2(state, step); 

    std::swap(state.S[state.i], state.S[state.j]);
    state.j = old_j;
    return result;
} 

bool guess_Si_2(State &state, int step) {
    stats->was[1][state.assigned]++;

    if (state.S[state.i] != -1) {
        stats->no_guess[1][state.assigned]++;
        return verify(state, step);
    } 
    state.assigned += 1;
    for (int Si = 0; Si < state.N; ++Si) {
        if (state.used[Si])
            continue;
        stats->guesses += 1;
        state.S[state.i] = Si;
        state.used[Si] = true;

        bool result = verify(state, step);
        
        state.used[Si] = false;
        if (result) {
            return result;
        }
    }
    state.S[state.i] = -1;
    state.assigned -= 1;
    return false;
}

bool verify(State &state, int step) {
    ASSERT(step < keystream.size(), "not enough keystream");

    int SiSj = (state.S[state.i] + state.S[state.j]) % state.N;
    int our_z = state.S[SiSj];
    int known_z = keystream[step];

    stats->was[2][state.assigned]++;
    stats->was[3][state.assigned]++;

    if (state.used[known_z]) {
        // known keystream is somewhere in permutation
        if (our_z == known_z) {
            stats->no_guess[2][state.assigned]++;

            bool result = start(state, step + 1);
            
            if (result) {
                return result;
            }
        }
    } else {
        // known_z is not in permutation
        if (our_z == -1) {
            stats->no_guess[3][state.assigned]++;

            ASSERT(state.used[known_z] == 0, "known_Z is in permutation, when it should not be");
            
            stats->guesses += 1;
            state.assigned += 1;
            
            state.S[SiSj] = known_z;
            state.used[known_z] = true;
            
            bool result = start(state, step + 1);
            
            state.S[SiSj] = -1;
            state.used[known_z] = false;
            state.assigned -= 1;
            
            if (result) {
                return result;
            }
        }
    }
    return false;
}

void backtrack(std::vector<int> &known_keystream, State &starting_state, State *& found_state, bool stop_after_found, Stats * backtrack_stats) {
    result_state = nullptr;
    result_step = 0;
    stop = stop_after_found;
    keystream = known_keystream;

    stats = backtrack_stats;

    State starting_state_copy(starting_state);

    start(starting_state_copy, 0);
    bool result = (result_state != nullptr);
    found_state = nullptr;

    if (result) {
        ASSERT(result_state != nullptr, "found result, but state is nullptr");
        RC4 cipher(result_state);
        cipher.inverse_state(result_step);
        found_state = result_state;
    }
}