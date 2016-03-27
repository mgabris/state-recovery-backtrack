# Spritz state recovery backtrack in python

This directory contains python implementation of state recovery backtrack for Spritz.

# Usage

### Generate states
Random states for both RC4 and Sprtiz backtracks are generated with script [generate.py](./generate.py). All options can be printed invoking this script with switch ```-h```.

Special state is availible only for Spritz.

#### Examples
To generate 1000 states for cipher RC4, with state size 16, 5 revealed values which are independent of actual state and with backtrack starting on offset of 8:

```bash
$python3 generate.py --rc4 --size 16 --preselected 5 --reveal_random --amount 1000 --prefix_length 8 > file
```

To generate 1000 special states for Spritz, with state size 64 with 20 random preselected values on even positions and 15 on odd positions:

```bash
$python3 generate.py --spritz --special --size 64 --preselected_even 20 --preselected_odd 15 --reveal_random --amount 1000 > file
```

### Test backtrack

To test Spritz backtrack optimizations, invoke [benchmark.py](./benchmark.py) with appropriate arguments, help can be printed out with switch ```-h```.

By default, after each run of benchmark, it will dump all stats into timestamp named file, it can be prevented with ```-nsl```. Stats file can be quite large for bigger experiments. To print past experiment stats, use [print_stats.py](./print_stats.py).

##### Note on paper terminology
To simulate complexity of estimate, switch ```-ns``` will force backtrack to continue even after correct state is found.

All prefix check optimizations can be turned on with ```-pc -pcc -pccw -pcg```.

Change order optimization is turned on with ```-lgo```. 

