#!/bin/bash

EX=$HOME/soft/pgn-extract/pgn-extract
OPTS="--fencomments"

$EX $OPTS $1 > fen.out
#python fen2stats.py
