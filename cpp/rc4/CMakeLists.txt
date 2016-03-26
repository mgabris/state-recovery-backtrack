cmake_minimum_required(VERSION 2.8.4)
project(rc4-backtrack)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -std=c++11")

# simple backtrack
set(SOURCE_FILES main.cpp backtrack.cpp RC4.cpp State.cpp Stats.cpp common.cpp)
add_executable(backtrack ${SOURCE_FILES})

# backtrack with change order optimization
set(SOURCE_FILES main.cpp backtrack_change.cpp RC4.cpp State.cpp Stats.cpp common.cpp)
add_executable(backtrack_change ${SOURCE_FILES})
