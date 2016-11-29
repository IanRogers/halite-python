#!/bin/bash

ME=$1
THEM=$2
PY=python3

rm -f *.log *.hlt

./halite -d "30 30" "$PY $ME" "$PY $THEM"

tail *.log
echo
