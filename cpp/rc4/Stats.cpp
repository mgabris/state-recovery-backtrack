#include <iostream>

#include "Stats.hpp"

Stats::Stats(int N, int k) : N(N), k(k), guesses(0) {
    for (int i = 0; i < k; ++i) {
        std::vector<int> wl(N+1, 0);
        std::vector<int> ngl(N+1, 0);
        was.push_back(wl);
        no_guess.push_back(ngl);
    }
}

AggregateStats::AggregateStats(int N, int k) : N(N), k(k), sum_guesses(0) {
    for (int i = 0; i < k; ++i) {
        std::vector<double> l1(N+1, 0);
        std::vector<int> l2(N+1, 0);
        no_guess_probabilities.push_back(l1);
        no_guess_counts.push_back(l2);
    }
}

void AggregateStats::add(Stats * stats) {
    sum_guesses += stats->guesses;
    for (int i = 0; i < k; ++i) {
        for (int j = 0; j <= N; ++j) {
            double v = 0;
            if (stats->was[i][j] != 0) {
                v = (double)stats->no_guess[i][j] / stats->was[i][j];
                no_guess_probabilities[i][j] += v;
                no_guess_counts[i][j] += 1;
            }
        }
    }
}

void AggregateStats::print() {
    for (int i = 0; i < k-1; ++i) {
        for (int j = 0; j < no_guess_probabilities[i].size(); ++j) {
            std::cout << i+1 << "-" << j << ": ";
            std::cout << no_guess_probabilities[i][j] / no_guess_counts[i][j];
            std::cout << " " << (double)(j) / (i<5 ? N : (N*N))<< std::endl;
        }
    }
    for (int j = 0; j < no_guess_probabilities[k-1].size(); ++j) {
        std::cout << k-1 << "-" << j << ": ";
        std::cout << no_guess_probabilities[k-1][j] / no_guess_counts[k-2][j];
        std::cout << " " << 1 - (double)(j) / N*N << std::endl;
    }
}