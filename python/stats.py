from math import log, sqrt
from collections import defaultdict

class Stats:

    class RunStats:
        def __init__(self):
            # number of times we assign value into permutation through backtrack algorithm
            self.guesses = 0
            # number of backtrack function calls
            self.backtrack_calls = 0
            # number of times bactrack gets to state, where he alredy guessed every
            # permutation value without prior conflict
            self.completely_filled = 0
            # number of times completely guessed state is not consistent with keystream
            # that comes right after it
            self.forward_check_failed = 0
            # number of times revert and prefix check occured
            self.prefix_checks = 0
            # number of times state was not consistent with prefix
            self.not_prefix_consistent = 0
            # list of depths, rounds of prefix check until conflict or None value
            self.prefix_checks_depths = []
            # list of results of prefix checks, corresponding depths are in 
            # prefix_checks_depths list
            self.prefix_checks_results = []
            # successful prefix checks (that gets to start of prefix without
            # conflict or unknown value
            self.prefix_checks_successful = 0
            # maximal recursion depth (start is 0 even with non-zero prefix)
            self.max_recursion_depth = 0
            # list of recursion depths when backtrack branches ended (start is 
            # 0 even with non-zero prefix)
            self.end_recursion_depths = []
            # running time of backtrack, in seconds
            self.time = 0
            # backtrack found nothing
            self.found = False
            # number of times when check for skip can start
            self.skip_last_guess_starts = 0
            # number of times when check for skip is positive
            self.skip_last_guess_continues = 0

    def __init__(self, argv=None):
        self.precision = 3
        self.argv = argv

    def add(self, run_stats):
        for attr, val in run_stats.__dict__.items():
            attr_list = self.__dict__.get(attr, [])
            attr_list.append(val)
            self.__dict__[attr] = attr_list

    def avg(array, precision=None):
        if  len(array) == 0:
            return 0
        result = sum(array) / len(array)
        if precision:
            result = round(result, precision)
        return result

    def avg_of_lists(array, precision=None):
        if len(array) == 0:
            return 0
        avgs = [Stats.avg(l) for l in array]
        return Stats.avg(avgs, precision)

    def deviation(array, precision=None):
        if len(array) < 2:
            # TODO: more apropriate value
            return 0

        avg = Stats.avg(array)
        error_sum = 0
        for el in array:
            error_sum += (el - avg)**2
        variance = error_sum / (len(array) - 1)
        standard_deviation = sqrt(variance)

        if precision:
            standard_deviation = round(standard_deviation, precision)
        return standard_deviation

    def avg_prefix_depth_distribution(self):
        depth_distr = defaultdict(int)
        for depths, results in zip(self.prefix_checks_depths, self.prefix_checks_results):
            for d, r in zip(depths, results):
                depth_distr[d] += 1
        for d in depth_distr:
            depth_distr[d] /= self.size
        return [depth_distr[i] for i in range(1, self.max_prefix_depth()+1)]

    def avg_prefix_depth_result_distribution(self):
        result_distr = defaultdict(lambda :defaultdict(int))
        for depths, results in zip(self.prefix_checks_depths, self.prefix_checks_results):
            for d, r in zip(depths, results):
                result_distr[r][d] += 1
        for r in result_distr:
            for d in result_distr[r]:
                result_distr[r][d] /= self.size
        result = {}
        for r in [None, False, True]:
            result[r] = [result_distr[r][i] for i in range(1, self.max_prefix_depth()+1)]
        return result

    def transpose_and_number(m):
        rows = len(m)
        cols = len(m[0])
        trans = [[0 for _ in range(rows+1)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                trans[c][r+1] = m[r][c]
        for r in range(cols):
            trans[r][0] = r+1
        return trans

    def transpose(m):
        rows = len(m)
        cols = len(m[0])
        trans = [[0 for _ in range(rows)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                trans[c][r] = m[r][c]
        return trans

    def avg_prefix_depth_distribution_table(self):
        total = Stats.avg(self.prefix_checks, self.precision)
        ended_depth = self.avg_prefix_depth_distribution()
        prefix_results = self.avg_prefix_depth_result_distribution()
        prefix_results_percent = defaultdict(list)
        for i in range(len(ended_depth)):
            prefix_results_percent['ended'].append(ended_depth[i] / total * 100)
            prefix_results_percent[None].append(prefix_results[None][i] / total * 100)
            prefix_results_percent[False].append(prefix_results[False][i] / total * 100)
        table = [
            range(1, len(ended_depth)+1),
            prefix_results_percent['ended'],
            prefix_results_percent[None],
            prefix_results_percent[False],
            ended_depth,
            prefix_results[None],
            prefix_results[False]
        ]
        return Stats.transpose(table)

    def max_prefix_depth(self):
        max_depth = -1
        for depths in self.prefix_checks_depths:
            if depths != []:
                max_depth = max(max_depth, max(depths))
        return max_depth

    @property
    def size(self):
        return len(self.guesses)
    
    def print_stats(self, verbosity):
        if verbosity == -1:
            for v in self.guesses:
                print(v)
        if verbosity == 0:
            # common values
            print([
                Stats.avg(self.guesses, self.precision),
                round(log(Stats.avg(self.guesses), 2), self.precision),
                Stats.deviation(self.guesses, self.precision),
                Stats.avg(self.completely_filled, self.precision),
                Stats.avg(self.forward_check_failed, self.precision),
                max(self.max_recursion_depth),
                Stats.avg_of_lists(self.end_recursion_depths, self.precision),  
                Stats.avg(self.time, self.precision)
            ])
            return
        if verbosity >= 1 and sum([1 if x else 0 for x in self.found]) < self.size:
            # not all states were successfully found
            print('NOT ALL STATES WERE FOUND')
        if verbosity == 1 or verbosity >= 3:
            # common values
            print([
                Stats.avg(self.guesses, self.precision),
                round(log(Stats.avg(self.guesses), 2), self.precision),
                Stats.deviation(self.guesses, self.precision),
                Stats.avg(self.completely_filled, self.precision),
                Stats.avg(self.forward_check_failed, self.precision),
                max(self.max_recursion_depth),
                Stats.avg_of_lists(self.end_recursion_depths, self.precision),  
                Stats.avg(self.time, self.precision)
            ])
            # time
            print([
                Stats.avg(self.time, self.precision),
                round(min(self.time), self.precision),
                round(max(self.time), self.precision)
            ])
            # prefix check common things
            print([
                Stats.avg(self.prefix_checks, self.precision),
                Stats.avg(self.not_prefix_consistent, self.precision),
                Stats.avg(self.prefix_checks_successful, self.precision),
                Stats.avg_of_lists(self.prefix_checks_depths, self.precision)
            ])
            # prefix check distributions
            table = self.avg_prefix_depth_distribution_table()
            print(table)
            if verbosity >=3:
                for l in table:
                    print(l)
            print([
                Stats.avg(self.prefix_checks, self.precision),
                Stats.avg(self.prefix_checks_successful, self.precision)
            ])
            # Knudsen's optimization
            print([
                Stats.avg(self.skip_last_guess_starts, self.precision),
                Stats.avg(self.skip_last_guess_continues, self.precision)
            ])
        if verbosity >= 2:
            print('experiments:', self.size)
            print('found state:', sum([1 if x else 0 for x in self.found]))
            print('avg guesses:', Stats.avg(self.guesses, self.precision))
            print('avg log guesses:', round(log(Stats.avg(self.guesses), 2), self.precision))
            print(
                'sample standard deviation',
                Stats.deviation(self.guesses, self.precision)
            )
            print('min guess:', min(self.guesses))
            print('max guess:', max(self.guesses))
            print('avg time:', Stats.avg(self.time, self.precision))
            print('min time:', min(self.time))
            print('max time:', max(self.time))
        if verbosity >= 3:
            print(
                'completely filled:',
                Stats.avg(self.completely_filled, self.precision)
            )
            print(
                'forward check failed:',
                Stats.avg(self.forward_check_failed, self.precision)
            )
            print(
                'skip last guess situations:',
                Stats.avg(self.skip_last_guess_starts, self.precision)
            )
            print(
                'skip last guess successful:',
                Stats.avg(self.skip_last_guess_continues, self.precision)
            )
            print('prefix checks:', Stats.avg(self.prefix_checks, self.precision))
            print(
                'avg prefix check depth distribution',
                self.avg_prefix_depth_distribution()
            )
            prefix_results = self.avg_prefix_depth_result_distribution()
            for r in [None, False, True]:
                print('avg prefix check depth results: '+ str(r) ,
                    prefix_results[r]
                )
            print(
                'max prefix depth:',
                self.max_prefix_depth()
            )
            print(
                'prefix check successful:',
                Stats.avg(self.prefix_checks_successful, self.precision)
            )
            print(
                'prefix check depths:',
                Stats.avg_of_lists(self.prefix_checks_depths, self.precision)
            )
            print('backtrack calls:', Stats.avg(self.backtrack_calls, self.precision))
            print(
                'max recursion depth:',
                max(self.max_recursion_depth)
            )
            print(
                'average end recursion depths',
                Stats.avg_of_lists(self.end_recursion_depths, self.precision)
            )
