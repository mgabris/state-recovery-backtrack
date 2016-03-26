#include <iostream>
#include <vector>
#include <string>

#include "common.h"

void print_vector(std::vector<int> v) {
    std::cout << "[";
    std::string delim = "";
    for (auto e : v) {
        std::cout << delim << e;
        delim = ", ";
    }
    std::cout << "]" << std::endl;
}

void print_array(int * a, int n) {
    std::cout << "[";
    std::string delim = "";
    for (int i = 0; i < n; ++i) {
        std::cout << delim << a[i];
        delim = ",";
    }
    std::cout << "]" << std::endl;
}