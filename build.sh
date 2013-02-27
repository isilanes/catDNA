#!/bin/bash

# Variables:
GCC=gcc
OPTS="-O3"

# Compile modules:
$GCC $OPTS -c src/corr.c
$GCC $OPTS -c src/board.c
$GCC $OPTS -c src/data.c
$GCC $OPTS -c src/eval.c
$GCC $OPTS -c src/search.c
$GCC $OPTS -c src/utils.c

# Main:
#$GCC $OPTS -o catDNA -g corr.o [bd-z]*.o src/main.c
$GCC $OPTS -o catDNA -g *.o src/main.c

# Clean:
rm -f *.o
