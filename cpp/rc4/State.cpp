#include <iostream>
#include <vector>

using namespace std;

#include "assert.h"

#include "State.hpp"


State::State(int N) {
    this->N = N;
    S.assign(N, -1);
    used.assign(N, 0);
    assigned = 0;
    i = j = 0;
};

State::State(vector<int> &registers, vector<int> &permutation) {
    set_registers(registers);
    set_permutation(permutation);
}

State::State(State &other) {
    N = other.N;
    // copy permutation
    S = other.S;
    used = other.used;
    assigned = other.assigned;
    // copy registers
    i = other.i;
    j = other.j;
};

vector<int> State::get_registers() {
    vector<int> r(2);
    r[0] = i;
    r[1] = j;
    return r;
};

void State::set_registers(vector<int> &r) {
    i = r[0];
    j = r[1];
}

void State::set_permutation(vector<int> &permutation) {
    N = permutation.size();
    S = permutation;
    used.assign(N, 0);
    assigned = 0;
    for (int i = 0; i < permutation.size(); ++i) {
        ASSERT(S[i] == permutation[i], "permutation vector not copied correctly");
        if (permutation[i] != -1) {
            used[permutation[i]] = 1;
            assigned += 1;
        }
    } 
}

bool State::operator==(State &o) {
    if (N != o.N) {
        return false;
    }
    if (!(S == o.S)) {
        return false; 
    }
    if (i != o.i || j != o.j) {
        return false;
    }
    return true;
}

void State::print_registers() {
    print_vector(get_registers());
}

void State::print_permutation() {
    print_vector(S);
}

void State::print()  {
    print_registers();
    print_permutation();
}