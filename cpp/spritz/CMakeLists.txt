cmake_minimum_required(VERSION 2.8.4)
project(spritz-backtrack)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -std=c++11")

set(SOURCE_FILES main.cpp backtrack.cpp Spritz.cpp State.cpp Stats.cpp common.cpp)
add_executable(backtrack ${SOURCE_FILES})

set(SOURCE_FILES main.cpp backtrack_special.cpp Spritz.cpp State.cpp Stats.cpp common.cpp)
add_executable(backtrack_special ${SOURCE_FILES})