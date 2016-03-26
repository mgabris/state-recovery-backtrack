#ifndef __STATS_H__
#define __STATS_H__

#include <vector>

struct Stats {
    int N, k;
    long long guesses;
    std::vector<std::vector<int>> was, no_guess;

    Stats(int N, int k);
};

class AggregateStats {
public:
    int N, k;
    std::vector<std::vector<double>> no_guess_probabilities;
    std::vector<std::vector<int>> no_guess_counts;
    long long sum_guesses;

    AggregateStats(int N, int k);

    void add(Stats * stats);
    void print();
};

#endif
