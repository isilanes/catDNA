#!/bin/bash

source run.conf

cutechess-cli \
    -fcp name=$EA cmd=$BASE/engines/$EA \
    -scp name=$EB cmd=$BASE/engines/$EB \
    -both tc=1+1 proto=xboard restart=on book=$BOOK \
    -games 20 -repeat -concurrency 4
