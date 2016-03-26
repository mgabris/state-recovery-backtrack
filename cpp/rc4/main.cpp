#include <iostream>
#include <sstream>
#include <algorithm>
#include <vector>
#include <string>
#include <tuple>
#include <random>
#include <chrono>
#include <cmath>
#include <ctime>
#include <cstdlib>

using namespace std;

#include "assert.h"
#include "common.h"

#include "State.hpp"
#include "RC4.hpp"
#include "Stats.hpp"

#include "backtrack.hpp"

// Parse state from python 2D array [[registers], [permutation]]
// Maybe a bit messy
State * parse_state(const string &line) {
    istringstream stream(line);
    char a, b;
    vector<int> registers, permutation;
    
    stream >> a >> b;
    ASSERT(a == '[' && b == '[', "wrong input");
    
    // parse registers
    string string_registers;
    getline(stream, string_registers, ']');
    istringstream stream_registers(string_registers);
    string s;
    while (getline(stream_registers, s, ',')) {
        registers.push_back(stoi(s));
    }
    ASSERT(registers.size() == 2, "there must be exactly 2 values for registers");

    stream >> a >> b;
    ASSERT(a == ',' && b == '[', "wrong input");

    // parse permutation
    string string_permutation;
    getline(stream, string_permutation, ']');
    istringstream stream_permutation(string_permutation);
    while (getline(stream_permutation, s, ',')) {
        if (s == "None" || s == " None") {
            permutation.push_back(-1);
        } else {
            permutation.push_back(stoi(s));
        }
    }    

    return new State(registers, permutation);
}

void read_input(vector<tuple<State*, State*, int>> &states) {
    string initial, revealed, offset;
    getline(cin, initial);
    getline(cin, revealed);
    getline(cin, offset);
    
    while (!cin.eof()) {
        ASSERT(stoi(offset) == 0, "non-zero offset is not currently supported");
        states.push_back(tuple<State*, State*, int>(
            parse_state(initial),
            parse_state(revealed),
            stoi(offset)
        ));

        getline(cin, initial);
        getline(cin, revealed);
        getline(cin, offset);
    }
}

int main(int argc, char * argv[]) {
    if (argc < 4 || argc > 5) {
        cout << "Usage: " << argv[0] << " [stop after state is found (0/1)] [verbosity] [random keysteam (0/1)] [seed(optional)]" << endl;
        return 1;
    }

    // Parameters
    // We expect argv[1] to be 0 or 1
    bool stop_after_found = (argv[1][0] == '1');
    int verbosity = atoi(argv[2]);
    bool random_keystream = (argv[3][0] == '1');
    unsigned seed;
    if (argc == 5) {
        seed = atoi(argv[4]);
    } else {
        seed = chrono::system_clock::now().time_since_epoch().count();
    }
    mt19937 generator;
    if (random_keystream) {
        if (verbosity >= 2) {
            cout << "seed: " << seed << endl;
        }
        generator.seed(seed);
    }

    vector<tuple<State*, State*, int>> states;
    read_input(states);

    bool ticks = true;
    int prompt_step = max(1, (int)states.size() / 20);
    long long sum_guesses = 0;
    int found_states = 0;
    clock_t elapsed_time = 0;
    int i = 0;
    int N = get<0>(states[0])->N;

    AggregateStats overall_stats(N, 4);

    for (auto e : states) {
        if (verbosity >= 2 && i % prompt_step == 0) {
            cout << "test #: " << i << endl;
        }
        ++i;

        ASSERT(N == get<0>(e)->N, "states are not of same size");
        State * initial_state = get<0>(e);
        State * revealed_state = get<1>(e);

        // generate keystream
        vector<int> known_keystream;
        if (random_keystream) {
            for (int i = 0; i < 10 * N; ++i) {
                known_keystream.push_back(generator() % N);
            }
        } else {
            // copy of inital state, as cipher modifies it
            State * tmp = new State(*initial_state);
            RC4 cipher(tmp);
            cipher.keystream(10 * N, known_keystream);
            delete tmp;
        }

        State * result_state = NULL;
        long long guesses = 0;
        Stats * stats = new Stats(N, 4);

        clock_t start = clock();
        backtrack(known_keystream, *revealed_state, result_state,stop_after_found, stats);
        elapsed_time += clock() - start;

        overall_stats.add(stats);

        if (verbosity == 1) {
            cout << stats->guesses << endl;
        }
        if (result_state != NULL) {
            found_states += 1;
            ASSERT(*result_state == *initial_state, "backtrack found different state");
            delete result_state;
        }
        delete stats;
    }

    if (verbosity >= 2) {
        long long sum_guesses = overall_stats.sum_guesses;
        cout << "guesses: " << sum_guesses << endl;
        cout << "avg guesses: " << (double)sum_guesses / states.size() << endl;
        cout << "log guesses: " << log2((double)sum_guesses / states.size()) << endl;
        cout << "found states: " << found_states << " / " << states.size() << endl;
        cout << "total time: " << ((float)elapsed_time) / CLOCKS_PER_SEC << endl;
        cout << "avg time: " << ((float)elapsed_time) / CLOCKS_PER_SEC / states.size() << endl;
    }

    if (verbosity >= 3) {
        overall_stats.print();
    }

    for (auto e : states) {
        delete get<0>(e);
        delete get<1>(e);
    }

    return 0;
}
