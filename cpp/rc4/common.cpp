#include <iostream>
#include <vector>
#include <string>

#include "common.h"

using namespace std;

void print_vector(vector<int> v) {
    cout << "[";
    string delim = "";
    for (auto e : v) {
        cout << delim << e;
        delim = ", ";
    }
    cout << "]" << endl;
}

void print_array(int * a, int n) {
    cout << "[";
    string delim = "";
    for (int i = 0; i < n; ++i) {
        cout << delim << a[i];
        delim = ",";
    }
    cout << "]" << endl;
}
