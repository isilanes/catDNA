#!/bin/bash

# Variables:
GCC=gcc
OPTS="-O3"
CFILES="board.c  data.c  eval.c  main.c  search.c  utils.c corr1.c"

# Compile:
$GCC $OPTS -o catDNA $CFILES
