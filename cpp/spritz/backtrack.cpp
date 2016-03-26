#include <iostream>

#include <algorithm>
#include <vector>
#include <string>

#include "assert.h"
#include "common.h"

#include "backtrack.hpp"

#include "Spritz.hpp"
#include "State.hpp"
#include "Stats.hpp"


std::vector<int> keystream;
State * result_state = nullptr;
int result_step = 0;
bool stop;
Stats * stats;

bool forward_correct(State &state, int start, int amount) {
    ASSERT(keystream.size() > start+amount+1, "need more keystream");

    State tmp(state);
    Spritz cipher(&tmp);
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
        if (forward_correct(state, step, 2 * state.N)) {
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
    state.i = (state.i + state.w) % state.N;

    bool result = guess_Si(state, step);

    state.i = old_i;
    return result;
}

bool guess_Si(State &state, int step) {
    stats->was[0][state.assigned]++;

    if (state.S[state.i] != -1) {
        stats->no_guess[0][state.assigned]++;
        return guess_SjSi(state, step);
    } 
    state.assigned += 1;
    for (int Si = 0; Si < state.N; ++Si) {
        if (state.used[Si])
            continue;
        stats->guesses += 1;
        state.S[state.i] = Si;
        state.used[Si] = true;

        bool result = guess_SjSi(state, step);

        state.used[Si] = false;
        if (result) {
            return result;
        }
    }
    state.S[state.i] = -1;
    state.assigned -= 1;
    return false;
}

bool guess_SjSi(State &state, int step) {
    stats->was[1][state.assigned]++;

    int jSi = (state.j + state.S[state.i]) % state.N;
    if (state.S[jSi] != -1) {
        stats->no_guess[1][state.assigned]++;
        return set_j(state, step);
    }
    state.assigned += 1;
    for (int SjSi = 0; SjSi < state.N; ++SjSi) {
        if (state.used[SjSi]) {
            continue;
        } 
        stats->guesses += 1;
        state.S[jSi] = SjSi;
        state.used[SjSi] = true;

        bool result = set_j(state, step);

        state.used[SjSi] = false;
        if (result) {
            return result;
        }
    }
    state.S[jSi] = -1;
    state.assigned -= 1;
    return false;
}

bool set_j(State &state, int step) {
    int old_j = state.j;
    int jSi = (state.j + state.S[state.i]) % state.N;
    state.j = (state.k + state.S[jSi]) % state.N;

    bool result = guess_Sj(state, step); 

    state.j = old_j;
    return result;
} 

bool guess_Sj(State &state, int step) {
    stats->was[2][state.assigned]++;

    if (state.S[state.j] != -1) {
        stats->no_guess[2][state.assigned]++;
        return set_k(state, step);
    } 
    state.assigned += 1;
    for (int Sj = 0; Sj < state.N; ++Sj) {
        if (state.used[Sj])
            continue;
        stats->guesses += 1;
        state.S[state.j] = Sj;
        state.used[Sj] = true;

        bool result = set_k(state, step);

        state.used[Sj] = false;
        if (result) {
            return result;
        }
    }
    state.S[state.j] = -1;
    state.assigned -= 1;
    return false;
}

bool set_k(State &state, int step) {
    int old_k = state.k;
    state.k = (state.i + state.k + state.S[state.j]) % state.N;
    std::swap(state.S[state.i], state.S[state.j]);

    bool result = guess_Szk(state, step);

    std::swap(state.S[state.i], state.S[state.j]);
    state.k = old_k;
    return result;
}

bool guess_Szk(State &state, int step) {
    stats->was[3][state.assigned]++;

    int zk = (state.z + state.k) % state.N;
    if (state.S[zk] != -1) {
        stats->no_guess[3][state.assigned]++;
        return guess_SiSzk(state, step);
    } 
    state.assigned += 1;
    for (int Szk = 0; Szk < state.N; ++Szk) {
        if (state.used[Szk])
            continue;
        stats->guesses += 1;
        state.S[zk] = Szk;
        state.used[Szk] = true;

        bool result = guess_SiSzk(state, step);

        state.used[Szk] = false;
        if (result) {
            return result;
        }
    }
    state.S[zk] = -1;
    state.assigned -= 1;
    return false;
}

bool guess_SiSzk(State &state, int step) {
    stats->was[4][state.assigned]++;

    int zk = (state.z + state.k) % state.N;
    int iSzk = (state.i + state.S[zk]) % state.N;
    if (state.S[iSzk] != -1) {
        stats->no_guess[4][state.assigned]++;
        return verify(state, step);
    } 
    state.assigned += 1;
    for (int SiSzk = 0; SiSzk < state.N; ++SiSzk) {
        if (state.used[SiSzk])
            continue;
        stats->guesses += 1;
        state.S[iSzk] = SiSzk;
        state.used[SiSzk] = true;

        bool result = verify(state, step);
        
        state.used[SiSzk] = false;
        if (result) {
            return result;
        }
    }
    state.S[iSzk] = -1;
    state.assigned -= 1;
    return false;   
}

bool verify(State &state, int step) {
    ASSERT(step < keystream.size(), "not enough keystream");

    stats->was[5][state.assigned]++;

    int zk = (state.z + state.k) % state.N;
    int iSzk = (state.i + state.S[zk]) % state.N;
    int jSiSzk = (state.j + state.S[iSzk]) % state.N;
    int our_z = state.S[jSiSzk];
    int known_z = keystream[step];

    if (state.used[known_z]) {
        // known keystream is somewhere in permutation
        if (our_z == known_z) {
            stats->no_guess[5][state.assigned]++;

            int old_z = state.z;
            state.z = known_z;

            bool result = start(state, step + 1);
            
            state.z = old_z;
            
            if (result) {
                return result;
            }
        }
    } else {
        // known_z is not in permutation
        if (our_z == -1) {
            ASSERT(state.used[known_z] == 0, "known_Z is in permutation, when it should not be");
            
            stats->guesses += 1;
            state.assigned += 1;
            
            state.S[jSiSzk] = known_z;
            state.used[known_z] = true;
            int old_z = state.z;
            state.z = known_z;
            
            if (step > 0) ASSERT(old_z == keystream[step-1], "");

            bool result = start(state, step + 1);
            
            state.z = old_z;
            state.S[jSiSzk] = -1;
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
        Spritz cipher(result_state);
        cipher.inverse_state(result_step);
        found_state = result_state;
    }
}