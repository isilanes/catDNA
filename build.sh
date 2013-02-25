#!/bin/bash

# Variables:
GCC=gcc
OPTS="-O3"
CFILES="corr.c board.c  data.c  eval.c  main.c  search.c  utils.c"

# Compile:
$GCC $OPTS -o catDNA $CFILES
