#ifndef __STATE_H__
#define __STATE_H__

#include <iostream>
#include <vector>

using namespace std;

#include "common.h"

struct State {
    int N;
    vector<int> S;
    vector<int> used;
    int i, j, k, z, a, w;
    int assigned;

    State(int N);
    State(vector<int> &registers, vector<int> &permutation);
    State(State &other);

    vector<int> get_registers();
    void set_registers(vector<int> &r);
    void set_permutation(vector<int> &permutation);

    bool operator==(State &o);

    void print_registers();
    void print_permutation();
    void print();
};

#endif