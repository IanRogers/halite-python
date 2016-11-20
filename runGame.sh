#!/bin/bash

rm -f *.log *.hlt

if hash python3 2>/dev/null; then
    PY=python3
else
    PY=python
fi

./halite -d "30 30" "$PY MyBot.py" "$PY Virus1.py"

tail *.log
echo
