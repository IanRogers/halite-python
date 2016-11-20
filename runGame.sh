#!/bin/bash

rm -f *.log *.hlt

if hash python3 2>/dev/null; then
    ./halite -d "30 30" "python3 MyBot.py" "python3 RandomBot.py"
else
    ./halite -d "30 30" "python MyBot.py" "python RandomBot.py"
fi

tail *.log
echo
