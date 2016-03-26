#ifndef __BACKTRACK_H__
#define __BACKTRACK_H__

#include <vector>
#include "State.hpp"
#include "Stats.hpp"

bool forward_correct(State &state, int start, int amount);

bool guess_Si(State &state, int step);
bool guess_Si_2(State &state, int step);

bool set_i(State &state, int step);
bool set_j(State &state, int step);

bool start(State &state, int step);
bool verify(State &state, int step);

void backtrack(
    std::vector<int> &known_keystream, 
    State &starting_state, 
    State *& found_state, 
    bool stop_after_found, 
    Stats * backtrack_stats);

#endif