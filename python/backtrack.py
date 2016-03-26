#!/usr/bin/python3

from copy import deepcopy
from time import time

from random import shuffle

from spritz.cipher import Spritz
from states import SpritzState
from stats import Stats

# Global variables used in bactrack functions (instead of sending these
# parameters in every call)
# These parameters should be properly set before calling any backtrack
keystream = None
N = 8
settings = None
stats = None
guess_order = None

# helper variables
prefix_rounds = 0
no_stop_result = None
n_results = 0

def forward_correct(depth, state, threshold):
    global keystream

    if len(keystream) < depth+1+threshold:
        print('need more keystream', depth+1+threshold - len(keystream))
        assert False
        # keystream += cipher.keystream(depth+1+threshold - len(keystream))
    
    c = Spritz(state=state.state)
    state_keystream = c.keystream(threshold)
    for i in range(threshold):
        if state_keystream[i] != keystream[depth+i]:
            return False
    return True

"""
return value:
    True - consistent
    False - not consistent
    None - missing some values from permutation, can't continue
"""
def consistent_with_prefix_word(state, i):
    global N, keystream
    global settings

    Szk = state.S[(keystream[i-1] + state.k) % N]
    if Szk is None:
        return None
    SiSzk = state.S[(state.i + Szk) % N]
    if SiSzk is None:
        return None
    z = state.S[(state.j + SiSzk) % N]
    if z is None:
        if keystream[i] not in state.free:
            return False
        if settings.prefix_check_continue_write:
            # now we know that state.S[(state.j + SiSzk) % N] == keystream[i]
            # must holds
            state.S[(state.j + SiSzk) % N] = keystream[i]
            state.free.remove(keystream[i])
            return True
        else:
            return None
    if z != keystream[i]:
        return False
    return True


"""
return value:
    True - consistent
    False - not consistent
    None - missing some values from permutation, can't continue
"""
def consistent_with_prefix(state, prefix_length):
    global N, keystream
    global stats, settings
    global prefix_rounds

    assert state.z == keystream[prefix_length-1]

    prefix_rounds = 0

    for i in range(prefix_length-1, 0, -1):
        prefix_rounds += 1

        consistent = consistent_with_prefix_word(state, i)
        if not settings.prefix_check_continue and (consistent in [None, False]):
            return consistent
        if settings.prefix_check_continue and consistent is False:
            # real conflict, not just 'we dont know'
            return False

        # state.z = keystream[i-1]
        state.swap()
        if state.S[state.j] is None:
            return None
        state.k = (state.k - state.i - state.S[state.j]) % N 
        if state.S[state.i] is None:
            return None
        val = (state.j - state.k) % N
        val_in_S = False
        for j, v in enumerate(state.S):
            if val == v:
                state.j = (j - state.S[state.i]) % N
                val_in_S = True
                break
        if not val_in_S:
            # this can be either missing value or not correct state
            return None
        state.i = (state.i - state.w) % N

    stats.prefix_checks_successful += 1
    return True


def prefix_check(start_state, depth):
    global stats, settings
    global prefix_rounds

    # TODO: warning: side effect of deep copy is correct free set in reverted
    # state, as in copying, it is recalculated from S
    # should be changed to be explicitly visible
    reverted_state = deepcopy(start_state)

    # stats
    old_successfull = stats.prefix_checks_successful

    consistent = consistent_with_prefix(reverted_state, settings.prefix_length)

    # statistics
    assert prefix_rounds >= 1
    stats.prefix_checks += 1

    stats.prefix_checks_depths.append(prefix_rounds)
    stats.prefix_checks_results.append(consistent)
    if consistent is True:
        pass
    else:
        stats.not_prefix_consistent += 1
        stats.end_recursion_depths.append(depth - settings.prefix_length)

    return consistent


"""
return: possible_to_skip_guess, result_of_recursion
"""
def guess_skip(depth, state):
    global N, keystream
    global start_state
    global stats, settings
    # assert:
    #   we are in situation, where known_z is not in S and SiSzk is None
    #   state is in start of backtrack
    ns = deepcopy(state)
    ns.i = (state.i + state.w) % N
    if ns.S[ns.i] is None:
        return False, False
    if ns.S[(ns.j + ns.S[ns.i]) % N] is None:
        return False, False
    ns.j = (ns.k + ns.S[(ns.j + ns.S[ns.i]) % N]) % N
    if ns.S[ns.j] is None:
        return False, False
    ns.k = (ns.i + ns.k + ns.S[ns.j]) % N
    ns.swap()

    if depth >= len(keystream):
        print('need more keystream')
        assert False
    known_z = keystream[depth]
    if ns.S[(ns.z + ns.k) % N] is None:
        return False, False
    if known_z in ns.free:
        return False, False
    SiSzk = ns.S[(ns.i + ns.S[(ns.z + ns.k) % N]) % N]
    if SiSzk is None:
        # TODO: O(N) search
        w = ns.S.index(known_z)
        SiSzk = (w - ns.j) % N
        if SiSzk not in ns.free:
            # contradiction, we can cut this branch off
            return True, False
        # assign value and move to next step
        stats.guesses += 1
        start_state.S[(ns.i + ns.S[(ns.z + ns.k) % N]) % N] = SiSzk
        if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
            start_state.S[(ns.i + ns.S[(ns.z + ns.k) % N]) % N] = None
            return True, False
        ns.S[(ns.i + ns.S[(ns.z + ns.k) % N]) % N] = SiSzk
        ns.free.remove(SiSzk)
        assert ns.S[(ns.j + ns.S[(ns.i + ns.S[(ns.z + ns.k) % N]) % N]) % N] == known_z

        ns.z = known_z
        found = backtrack(depth + 1, ns)
        if found:
            return True, found
        ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
        start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
        return True, False
    if ns.S[(ns.j + SiSzk) % N] == known_z:
        #  SiSzk is already determined, so we cant continue, as we would
        # make 1 less guess
        return False, False
    # conflict, we can cut this branch, as no guessing can avoid it
    return True, False


def backtrack(depth, state):
    global N, keystream, start_state, guess_order
    global settings, stats
    global prefix_rounds
    global no_stop_result, n_results

    stats.backtrack_calls += 1
    if depth - settings.prefix_length > stats.max_recursion_depth:
        stats.max_recursion_depth = depth - settings.prefix_length

    if not state.free:
        stats.completely_filled += 1
        stats.end_recursion_depths.append(depth - settings.prefix_length)
        # we have filled the permutation, test if it's correct
        if forward_correct(depth, state, N):
            if settings.no_stop:
                n_results += 1
                no_stop_result = (depth, deepcopy(state))
                return False
            else:
                return depth, state
        stats.forward_check_failed += 1
        return False

    # new copy of state, only this copy will be modified and sent to recursion
    # CipherState in argument (state) will not be modified, only read
    ns = deepcopy(state)
    
    if settings.prefix_check and not settings.prefix_check_guess:
        # check for consistency with prefix
        if prefix_check(start_state, depth) is False:
            return False

    # actual guessing
    for Si in guess_order:
        ns.i = (state.i + state.w) % N

        end_Si = False
        assigned_Si = False
        if ns.S[ns.i] is None:
            if Si in ns.free:
                stats.guesses += 1
                start_state.S[ns.i] = Si
                if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                    start_state.S[ns.i] = None
                    continue
                ns.S[ns.i] = Si
                ns.free.remove(Si)
                assigned_Si = True
            else:
                continue
        else:
            end_Si = True

        for SjSi in guess_order:
            end_SjSi = False
            assigned_SjSi = False
            if ns.S[(state.j + ns.S[ns.i]) % N] is None:
                if SjSi in ns.free:
                    stats.guesses += 1
                    start_state.S[(state.j + ns.S[ns.i]) % N] = SjSi
                    if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                        start_state.S[(state.j + ns.S[ns.i]) % N] = None
                        continue
                    ns.S[(state.j + ns.S[ns.i]) % N] = SjSi
                    ns.free.remove(SjSi)
                    assigned_SjSi = True
                else:
                    continue
            else:
                end_SjSi = True

            ns.j = (state.k + ns.S[(state.j + ns.S[ns.i]) % N]) % N  

            for Sj in guess_order:
                end_Sj = False
                assigned_Sj = False
                if ns.S[ns.j] is None:
                    if Sj in ns.free:
                        stats.guesses += 1
                        start_state.S[ns.j] = Sj
                        if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                            start_state.S[ns.j] = None
                            continue
                        ns.S[ns.j] = Sj
                        ns.free.remove(Sj)
                        assigned_Sj = True
                    else:
                        continue
                else:
                    end_Sj = True

                ns.k = (ns.i + state.k + ns.S[ns.j]) % N
                # swap 
                assert ns.S[ns.i] is not None
                assert ns.S[ns.j] is not None
                ns.S[ns.i], ns.S[ns.j] = ns.S[ns.j], ns.S[ns.i]

                for Szk in guess_order:
                    end_Szk = False
                    assigned_Szk = False
                    if ns.S[(state.z + ns.k) % N] is None:
                        if Szk in ns.free:
                            stats.guesses += 1
                            start_state.S[(state.z + ns.k) % N] = Szk
                            if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                start_state.S[(state.z + ns.k) % N] = None
                                continue
                            ns.S[(state.z + ns.k) % N] = Szk
                            ns.free.remove(Szk)
                            assigned_Szk = True
                        else:
                            continue
                    else:
                        end_Szk = True

                    if settings.last_guess_order:
                        if depth >= len(keystream):
                            print('need more keystream')
                            assert False
                        
                        known_z = keystream[depth]

                        if known_z not in ns.free:
                            # known_z is in permutation
                            w = ns.S.index(known_z)
                            assert ns.S[w] == known_z
                            SiSzk = (w - ns.j) % N

                            assigned_SiSzk = False
                            contradiction = False
                            if ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] is None:
                                if SiSzk not in ns.free:
                                    # contradiction, as SiSzk is not in it's place
                                    contradiction = True
                                if not contradiction:
                                    # SiSzk can be guessed into permutation
                                    stats.guesses += 1
                                    start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                    if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                        # contradiction, not prefix consistent
                                        start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                        contradiction = True
                                    if not contradiction:
                                        ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                        ns.free.remove(SiSzk)
                                        assigned_SiSzk = True
                            else:
                                if ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] != SiSzk:
                                    # contradiction, SiSzk is alredy assigned, but with wrong value
                                    contradiction = True
                            if not contradiction:
                                our_z = ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N]
                                if our_z == known_z:
                                    ns.z = our_z
                                    found = backtrack(depth + 1, ns)
                                    if found:
                                        return found
                                else:
                                    # contradiction, as known_z is in permutation, it must be == our_z
                                    pass

                            if assigned_SiSzk:
                                ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                ns.free.add(SiSzk)
                        else:
                            # known_z not in permutation
                            assert known_z in ns.free
                            if ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] is not None:
                                # SiSzk is alredy known
                                # thus we know index of known_z
                                jSiSzk = (ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N
                                contradiction = False
                                if ns.S[jSiSzk] is not None:
                                    # contradiction, as known_z is not in S, so element at it's index must be None
                                    contradiction = True
                                if not contradiction:
                                    assert ns.S[jSiSzk] is None
                                    # everything determined, we can assign known_z value
                                    # to permutation and call recursion
                                    stats.guesses += 1                                
                                    start_state.S[jSiSzk] = known_z
                                    if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                        # contradiction, not prefix consistent
                                        start_state.S[jSiSzk] = None
                                        contradiction = True
                                    if not contradiction:
                                        ns.S[jSiSzk] = known_z
                                        ns.free.remove(known_z)
                                        ns.z = known_z

                                        found = backtrack(depth + 1, ns)
                                        if found:
                                            return found

                                        ns.S[jSiSzk] = None
                                        start_state.S[jSiSzk] = None
                                        ns.free.add(known_z)
                            else:
                                assert ns.S[(state.z + ns.k) % N] is not None
                                # known_z is not in permutation, SiSzk is None
                                # guess it's place
                                skip_guessing = False
                                if settings.skip_last_guess:
                                    stats.skip_last_guess_starts += 1
                                    ns.z = known_z
                                    skip_guessing, recursion_result = guess_skip(depth+1, ns)
                                    if skip_guessing:
                                        stats.skip_last_guess_continues += 1
                                    if skip_guessing and recursion_result:
                                        return recursion_result

                                if not settings.skip_last_guess or (settings.skip_last_guess and not skip_guessing):
                                    for pos, v in enumerate(ns.S):
                                        contradiction = False
                                        SiSzk = ((pos - ns.j) % N)
                                        if (v is not None) or (SiSzk not in ns.free):
                                            # not suitable position for known_z
                                            continue
                                        # pos is suitable position for known_z
                                        stats.guesses += 1
                                        start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                        if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                            # contradiction, not prefix consistent
                                            start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                            continue

                                        ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                        ns.free.remove(SiSzk)

                                        assert ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] is None or ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] == SiSzk
                                        assigned_SjSiSzk = False
                                        if ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] is None:
                                            # place where known_z should be is None
                                            if known_z not in ns.free:
                                                assert known_z == SiSzk
                                                # conflict
                                                contradiction = True
                                            if not contradiction:
                                                stats.guesses += 1
                                                start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = known_z
                                                if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                                    # contradiction, not prefix consistent
                                                    start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                                    contradiction = True
                                                if not contradiction:
                                                    ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = known_z
                                                    ns.free.remove(known_z)
                                                    assigned_SjSiSzk = True
                                        else:
                                            if ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] != known_z:
                                                contradiction = True

                                        if not contradiction:
                                            ns.z = known_z
                                            found = backtrack(depth + 1, ns)
                                            if found:
                                                return found

                                        if assigned_SjSiSzk:
                                            ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                            start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                            ns.free.add(known_z)

                                        ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                        start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                        ns.free.add(SiSzk)

                    else:
                        # guess every S value, then check for conflicts
                        for SiSzk in guess_order:
                            end_SiSzk = False
                            assigned_SiSzk = False

                            if ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] is None:
                                if SiSzk in ns.free:
                                    stats.guesses += 1
                                    start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                    if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                        start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                        continue
                                    ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = SiSzk
                                    ns.free.remove(SiSzk)
                                    assigned_SiSzk = True
                                else:
                                    continue
                            else:
                                end_SiSzk = True

                            our_z = ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N]
                            if depth >= len(keystream):
                                print('need more keystream')
                                assert False

                            assert depth < len(keystream)

                            known_z = keystream[depth]

                            # checks for consistecy with known keystream
                            if known_z not in ns.free:
                                # known keystream value is somewhere in permutation
                                if our_z == known_z:
                                    ns.z = our_z
                                    found = backtrack(depth + 1, ns)
                                    if found and not settings.no_stop:
                                        return found
                                else:
                                    # contradiction
                                    pass
                            else:
                                # we have not used known_z
                                if our_z is None:
                                    stats.guesses += 1
                                    start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = known_z
                                    if settings.prefix_check_guess and prefix_check(start_state, depth) is False:
                                        start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                    else:
                                        ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = known_z
                                        ns.free.remove(known_z)
                                        ns.z = known_z
                                        found = backtrack(depth + 1, ns)
                                        if found and not settings.no_stop:
                                            return found
                                        ns.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                        start_state.S[(ns.j + ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N]) % N] = None
                                        ns.free.add(known_z)
                                else:
                                    # contradiction
                                    pass

                            if assigned_SiSzk:
                                ns.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                start_state.S[(ns.i + ns.S[(state.z + ns.k) % N]) % N] = None
                                ns.free.add(SiSzk)
                            if end_SiSzk:
                                break

                    if assigned_Szk:
                        ns.S[(state.z + ns.k) % N] = None
                        start_state.S[(state.z + ns.k) % N] = None
                        ns.free.add(Szk)
                    if end_Szk:
                        break

                # swap back
                ns.S[ns.i], ns.S[ns.j] = ns.S[ns.j], ns.S[ns.i]

                if assigned_Sj:
                    ns.S[ns.j] = None
                    start_state.S[ns.j] = None
                    ns.free.add(Sj)
                if end_Sj:
                    break

            if assigned_SjSi:
                ns.S[(state.j + ns.S[ns.i]) % N] = None
                start_state.S[(state.j + ns.S[ns.i]) % N] = None
                ns.free.add(SjSi)
            if end_SjSi:
                break

        if assigned_Si:
            ns.S[ns.i] = None
            start_state.S[ns.i] = None
            ns.free.add(Si)
        if end_Si:
            break

    stats.end_recursion_depths.append(depth - settings.prefix_length)
    return False


# 'main' functions, entry points to backtrack algorithms
# need to set module's global variables, etc
def kpa(known_keystream, backtrack_state, kpa_settings):
    global N, keystream, start_state, guess_order
    global settings, stats

    # helper global variables
    global prefix_rounds
    global no_stop_result, n_results

    N = backtrack_state.size
    keystream = known_keystream
    start_state = deepcopy(backtrack_state) 
    guess_order = range(N)
    if kpa_settings.keystream_guess_order:
        assert len(keystream) >= N
        guess_order = []
        s = set()
        for w in keystream[:N]:
            if w not in s:
                s.add(w)
                guess_order.append(w)
        guess_order += list(set(range(N)) - s)
        assert sorted(guess_order) == list(range(N))

    settings = kpa_settings
    stats = Stats.RunStats()

    # helper global variables
    prefix_rounds = 0
    no_stop_result = False
    n_results = 0
    result = False
    
    start = time()
    if settings.no_stop:
        # result (if found) will be in global variable no_stop_result
        # as we dont return from backtrack when correct state is found
        backtrack(settings.prefix_length, backtrack_state)
        result = no_stop_result
    else:
        result = backtrack(settings.prefix_length, backtrack_state)
    elapsed = time() - start
    stats.time = elapsed
    
    if result is False:
        # not found correct state
        return None, stats

    if settings.no_stop:
        assert n_results == 1

    stats.found = True
    depth, found_state = result
    stats.depth = depth

    cipher = Spritz(found_state.state)
    cipher.inverse_state(depth)

    return SpritzState(cipher.state), stats
