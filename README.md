# state-recovery-backtrack
Implementation of state-recovery backtrack attacks for ciphers RC4 and Spritz.

Details about attacks can be found in our [paper -- TODO link]()

## Python code
Python implementation contains state-recovery of cipher Spritz, used for testing possible optimizations. 

It contains (apart from other) simple backtracktrack as well as change order and prefix check optimizations mentioned in paper.

## C++ code
C++ implementation is for both RC4 and Spritz. 

It contains basic backtrack and change order opotimization for RC4, basic and special state backtracks for Spritz. 
