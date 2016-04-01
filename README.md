# state-recovery-backtrack
Implementation of state-recovery backtrack attacks for ciphers RC4 and Spritz.

Details about attacks can be found in our [paper](https://eprint.iacr.org/2016/337)

## Python code
Python implementation contains state-recovery of cipher Spritz, used for testing possible optimizations. 

It contains (apart from other) simple backtracktrack as well as change order and prefix check optimizations mentioned in the paper.

#### Note
As code in python was used to experiment with different optimizations, we recommend to look at cleaner C++ code first.

## C++ code
C++ implementation is for both RC4 and Spritz. 

It contains basic backtrack and change order opotimization for RC4, basic and special state backtracks for Spritz. 
