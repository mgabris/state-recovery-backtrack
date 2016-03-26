#ifndef __RC4_H__
#define __RC4_H__

#include <algorithm>
#include <vector>


#include <cstdint>

#include "State.hpp"

class RC4
{
public:
    RC4(State * state);

    void keystream(int r, std::vector<int> &keystream);
    void inverse_state(int steps);
private:
    State * state;

    int gcd(int a, int b) {
        while (b != 0) {
            a = b;
            b = a % b;
        }
        return a;
    }

    int prg();

    // inverse operations
    void inverse_prg();
};


#endif