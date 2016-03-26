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
    i = j = k = z = a = 0;
    w = 1;
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
    i = other.i; j = other.j; k = other.k;
    z = other.z; a = other.a; w = other.w;
};

vector<int> State::get_registers() {
    vector<int> r(6);
    r[0] = i; r[1] = j; r[2] = k;
    r[3] = z; r[4] = a; r[5] = w;
    return r;
};

void State::set_registers(vector<int> &r) {
    i = r[0]; j = r[1]; k = r[2];
    z = r[3]; a = r[4]; w = r[5];
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
    if (i != o.i || j != o.j || k != o.k || z != o.z || a != o.a || w != o.w) {
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