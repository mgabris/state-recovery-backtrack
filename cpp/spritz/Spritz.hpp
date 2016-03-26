#ifndef __SPRITZ_H__
#define __SPRITZ_H__

#include <algorithm>
#include <vector>


#include <cstdint>

#include "State.hpp"

class Spritz
{
public:
    Spritz(State * state);

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

    // TODO(maybe): we dont really need key setup for backtrack
    // void absorb(std::vector<int> I);
    // void absorb_byte(int i);
    // void absorb_nibble(int x);
    // void absorb_stop();
    void shuffle();
    // void whip(r);
    // void crush();

    void squeeze(int r, std::vector<int> &keystream);
    int drip();
    void update();
    int output();

    // inverse operations
    void inverse_update();
    void inverse_output();
    void inverse_drip();
};


#endif