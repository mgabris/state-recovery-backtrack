#include <random>
#include <iostream>
#include <chrono>

using namespace std;

int main() {

    unsigned seed = chrono::system_clock::now().time_since_epoch().count();
    cout << "unsinged seed: " << seed << endl;
    // int seed = 47;
    // mt19937 generator(seed);
    mt19937 generator(3506755237);

    for (int i = 0; i < 5; ++i) {
        cout << generator() << endl;
    }

    return 0;
}