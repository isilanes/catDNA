#!/bin/bash

source run.conf

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUTEBASE/lib $CUTEBASE/cutechess-cli \
    -engine name=$EA cmd=$BASE/engines/$EA \
    -engine name=$EB cmd=$BASE/engines/$EB \
    -each tc=1+4 proto=xboard restart=on book=$BOOK \
    -games $ROUNDS -repeat -concurrency 4 -recover -wait 1000 -pgnout run.pgn
